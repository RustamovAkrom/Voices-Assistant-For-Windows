"""
Optimized main.py for Jarvis-like assistant.

Features:
- Threaded TTS and recognizer workers
- speaking Event to avoid recognizing own speech
- wake-word detection with regex-word boundaries
- active-mode with timeout that refreshes on commands
- safe skill/context passing
- graceful shutdown and reload commands
"""

import time
import re
import threading
import queue
import logging
from typing import Optional

from src.core.recognizer import Recognizer
from src.core.tts import HybridTTS
from src.core.skill_manager import SkillManager
from src.core.executor import Executor
from src.core.config import get_settings

# -----------------------
# Logger
# -----------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("Jarvis")

# -----------------------
# Globals / Queues / Events
# -----------------------
tts_queue: "queue.Queue[tuple[str, Optional[str]]]" = queue.Queue()
recognizer_queue: "queue.Queue[tuple[str, Optional[str]]]" = queue.Queue()
SHUTDOWN = threading.Event()
SPEAKING = threading.Event()          # set while TTS playing to avoid self-recognition
WORKERS: list[threading.Thread] = []

# Tunables (можете менять в config.yaml)
DEFAULT_ACTIVE_TIMEOUT = 20.0         # seconds assistant stays active after wake
RECOGNIZER_BACKOFF = 0.12             # sleep between recognizer loop iterations
MISUNDERSTAND_LIMIT = 3               # сколько подряд пустых распознаваний -> prompt

# -----------------------
# TTS worker
# -----------------------
def tts_worker(tts: HybridTTS):
    """
    Дочерний поток для последовательного озвучивания.
    Помечает SPEAKING во время воспроизведения, чтобы распознаватель игнорировал свои же звуки.
    """
    logger.debug("TTS worker started")
    while not SHUTDOWN.is_set():
        try:
            item = tts_queue.get(timeout=0.5)
        except queue.Empty:
            continue

        try:
            text, lang = item
            if not text:
                continue
            # set speaking flag so recognizer can skip audio while we output
            SPEAKING.set()
            logger.info(f"[TTS] Speaking ({lang}): {text}")
            try:
                # HybridTTS.speak is blocking (plays and waits)
                tts.speak(text, lang)
            except Exception as e:
                logger.exception(f"[TTS ERROR] {e}")
            finally:
                # small safety sleep to let audio device drain
                time.sleep(0.12)
                SPEAKING.clear()
        finally:
            tts_queue.task_done()
    logger.info("TTS worker stopped")


# -----------------------
# Recognizer worker
# -----------------------
def recognizer_worker(recognizer: Recognizer, silence_threshold: float = 3.0):
    """
    Простая, но надежная логика для распознавания.
    - слушает готовые куски текста из Recognizer.listen_text()
    - если SPEAKING установлен — отбрасывает результат (мы говорим сами)
    - помещает распознанные фразы в recognizer_queue
    """
    logger.debug("Recognizer worker started")
    misunderstand_count = 0

    while not SHUTDOWN.is_set():
        try:
            # listen_text() должен быстро возвращать либо ("", lang) либо (text, lang)
            result = recognizer.listen_text()
        except Exception as e:
            logger.exception(f"[Recognizer ERROR] {e}")
            time.sleep(0.5)
            continue

        if SPEAKING.is_set():
            # если ассистент сейчас говорит — игнорируем распознавание (предотвращает "слышит сам себя")
            logger.debug("Recognizer skipped because assistant is speaking")
            time.sleep(RECOGNIZER_BACKOFF)
            continue

        if not result:
            # пустой результат — увеличиваем счётчик и, при достижении порога, уведомляем
            misunderstand_count += 1
            if misunderstand_count >= MISUNDERSTAND_LIMIT:
                # делаем мягкий подсказ
                try:
                    recognizer_queue.put(("", None))
                except Exception:
                    pass
                misunderstand_count = 0
            time.sleep(RECOGNIZER_BACKOFF)
            continue

        # сбрасываем счётчик непонятых при реальном результате
        misunderstand_count = 0

        text, lang = result
        if not text:
            # иногда listen_text возвращает ("", lang)
            time.sleep(RECOGNIZER_BACKOFF)
            continue

        # нормализация
        text = text.strip()
        if not text:
            continue

        try:
            recognizer_queue.put((text, lang))
            logger.debug(f"Recognizer -> queue: ({lang}) {text}")
        except Exception as e:
            logger.exception(f"Failed to queue recognition result: {e}")
            time.sleep(RECOGNIZER_BACKOFF)

    logger.info("Recognizer worker stopped")


# -----------------------
# Helpers
# -----------------------
def build_wake_words(config: dict) -> set:
    wake_words = set()
    wake_cfg = config.get("wake_words", {}) or {}
    if isinstance(wake_cfg, dict):
        for lang_words in wake_cfg.values():
            if isinstance(lang_words, (list, tuple)):
                for w in lang_words:
                    wake_words.add(w.lower().strip())
    # backward compat
    single = config.get("wake_word")
    if single:
        wake_words.add(str(single).lower().strip())
    return wake_words


def remove_wake_word(text: str, wake_word: Optional[str]) -> str:
    if not text:
        return ""
    if not wake_word:
        return text.strip().lower()
    # use word boundaries to avoid accidental partial matches
    cleaned = re.sub(rf"\b{re.escape(wake_word)}\b", "", text, flags=re.IGNORECASE)
    return cleaned.strip().lower()


def is_reload_command(text: str, meta: dict, key: str) -> bool:
    if not (text and meta):
        return False
    patterns = meta.get(key, {}).get("patterns", []) or []
    return any(text == p.lower() for p in patterns)


# -----------------------
# Text processing core
# -----------------------
def process_text(executor: Executor, dataset: dict, skills: SkillManager,
                 text: str, lang: Optional[str], wake_words: set, active_state: dict):
    """
    Главная логика: wake-word -> activation -> commands -> execution
    active_state = { "active": bool, "last": float, "timeout": float }
    """
    if not text:
        # empty text used as a 'prompt' for user to repeat
        logger.debug("Empty prompt received (user silent)")
        return

    normalized = text.lower().strip()
    lang = (lang or active_state.get("lang") or "ru").lower()
    logger.info(f"🧠 Распознано ({lang}): {normalized}")

    # If not active — check wake words
    if not active_state["active"]:
        # find whole-word wake
        triggered = next((w for w in wake_words if re.search(rf"\b{re.escape(w)}\b", normalized)), None)
        if triggered:
            cleaned = remove_wake_word(normalized, triggered)
            # go active and update timer
            active_state["active"] = True
            active_state["last"] = time.time()
            active_state["lang"] = lang
            logger.info(f"🚀 Wake word activated: '{triggered}' (lang={lang})")
            # If there's immediate content after wake, execute it
            if cleaned:
                logger.info(f"🚀 Immediate command after wake: {cleaned}")
                _execute_and_respond(executor, skills, dataset, cleaned, lang)
            else:
                # acknowledgement
                tts_queue.put(("Слушаю вас.", lang))
        else:
            logger.debug("No wake word detected and assistant inactive -> ignoring")
        return

    # if active: check timeout
    if time.time() - active_state["last"] > active_state["timeout"]:
        logger.info("😴 Active timeout expired. Deactivating.")
        active_state["active"] = False
        return

    # refresh last active time on any recognized text
    active_state["last"] = time.time()

    # remove wake word if present in ongoing conversation
    triggered = next((w for w in wake_words if re.search(rf"\b{re.escape(w)}\b", normalized)), None)
    cleaned_text = remove_wake_word(normalized, triggered) if triggered else normalized

    if not cleaned_text:
        # nothing after wake word
        tts_queue.put(("Да, я слушаю.", lang))
        return

    meta = dataset.get("meta", {}) or {}

    # special meta commands (reload dataset, restart skills)
    if is_reload_command(cleaned_text, meta, "reload_dataset"):
        logger.info("🔁 Reload dataset command received")
        settings = get_settings()
        dataset = settings.dataset
        executor.update_dataset(dataset)
        skills.reload()
        resp = meta.get("reload_dataset", {}).get("response", {}).get(lang, "Датасет обновлён.")
        tts_queue.put((resp, lang))
        return

    if is_reload_command(cleaned_text, meta, "restart_skills"):
        logger.info("🔁 Restart skills command received")
        skills.reload()
        resp = meta.get("restart_skills", {}).get("response", {}).get(lang, "Навыки перезапущены.")
        tts_queue.put((resp, lang))
        return

    # run the command(s) via Executor
    _execute_and_respond(executor, skills, dataset, cleaned_text, lang)


def _execute_and_respond(executor: Executor, skills: SkillManager, dataset: dict, text: str, lang: str):
    """
    Выполняет Executor.handle (который использует matcher и SkillManager),
    и отправляет ответ в tts_queue. Если ответ уже приходит как dict (multi-lang),
    пытаемся взять ответ по lang.
    """
    try:
        response = executor.handle(text, lang=lang)
    except Exception as e:
        logger.exception(f"Executor error: {e}")
        response = {
            "ru": "Произошла ошибка при выполнении команды.",
            "en": "An error occurred executing the command.",
            "uz": "Buyruqni bajarishda xato yuz berdi."
        }.get(lang, "Ошибка.")

    # response can be a dict (meta) or string
    if isinstance(response, dict):
        out = response.get(lang) or response.get("en") or next(iter(response.values()), "")
    else:
        out = str(response) if response is not None else ""

    if out:
        tts_queue.put((out, lang))
    else:
        tts_queue.put(("Не понял, повторите.", lang))


# -----------------------
# Orchestrator / main
# -----------------------
def main():
    settings = get_settings()
    config = settings.config or {}
    dataset = settings.dataset or {}

    # init components
    recognizer = Recognizer(config)
    tts = HybridTTS(config)

    # context that will be passed into SkillManager (so skills can access config/dataset/tts/etc.)
    context = {"config": config, "dataset": dataset, "workers": WORKERS, "tts": tts}
    skills = SkillManager(context=context)
    executor = Executor(dataset, skills, config=config)

    wake_words = build_wake_words(config)
    logger.info(f"🎧 Wake words: {', '.join(sorted(wake_words)) or 'NONE'}")

    # start workers
    t_worker = threading.Thread(target=tts_worker, args=(tts,), daemon=True, name="TTS-Worker")
    r_worker = threading.Thread(target=recognizer_worker, args=(recognizer,), daemon=True, name="Recognizer-Worker")
    t_worker.start()
    r_worker.start()
    WORKERS.extend([t_worker, r_worker])

    # active state
    active_state = {"active": False, "last": 0.0, "timeout": config.get("assistant", {}).get("active_timeout", DEFAULT_ACTIVE_TIMEOUT), "lang": config.get("assistant", {}).get("default_language", "ru")}

    logger.info("🤖 Jarvis started and listening...")

    try:
        while not SHUTDOWN.is_set():
            try:
                text, lang = recognizer_queue.get(timeout=0.2)
            except queue.Empty:
                continue

            # process_text does internal checks for active state, wake words etc.
            try:
                process_text(executor, dataset, skills, text, lang, wake_words, active_state)
            except Exception as e:
                logger.exception(f"[PROCESS ERROR] {e}")
            finally:
                recognizer_queue.task_done()

    except KeyboardInterrupt:
        logger.info("🛑 KeyboardInterrupt — shutting down...")

    finally:
        # Graceful shutdown
        SHUTDOWN.set()
        logger.info("Waiting for queues to drain...")
        try:
            tts_queue.join()
        except Exception:
            pass
        logger.info("Stopping workers...")
        # If Recognizer has stop method, call it
        try:
            recognizer.stop()
        except Exception:
            pass

        for w in WORKERS:
            if w.is_alive():
                logger.debug(f"Joining worker {w.name}")
                w.join(timeout=1.0)

        logger.info("Jarvis stopped.")


if __name__ == "__main__":
    main()

# import time
# import re
# import threading
# import queue
# import logging

# from src.core.recognizer import Recognizer
# from src.core.tts import HybridTTS
# from src.core.skill_manager import SkillManager
# from src.core.executor import Executor
# from src.core.config import get_settings

# # === Настройка логирования ===
# logging.basicConfig(
#     level=logging.INFO,
#     format="[%(asctime)s] [%(levelname)s] %(message)s",
#     datefmt="%H:%M:%S",
# )
# logger = logging.getLogger("Jarvis")

# # === Очереди и глобальные состояния ===
# WORKERS = []
# tts_queue = queue.Queue()
# recognizer_queue = queue.Queue()


# # === Поток TTS ===
# def tts_worker(tts: HybridTTS):
#     """Обрабатывает очередь озвучки"""
#     while True:
#         text, lang = tts_queue.get()
#         try:
#             if text:
#                 tts.speak(text, lang)
#         except Exception as e:
#             logger.error(f"[TTS ERROR] {e}")
#         finally:
#             tts_queue.task_done()

# def recognizer_worker(recognizer: Recognizer, silence_threshold=3.0):
#     """
#     Базовая рабочая логика — сразу помещаем распознанные фразы в очередь.
#     (Более сложная агрегация по паузе можно вернуть позднее)
#     """
#     miss_count = 0
#     miss_threshold = 3

#     while True:
#         try:
#             result = recognizer.listen_text()
#             if result:
#                 miss_count = 0
#                 text, lang = result
#                 if text:
#                     recognizer_queue.put((text.strip(), lang))
#             else:
#                 miss_count += 1
#                 if miss_count >= miss_threshold:
#                     tts_queue.put(("Извини, я не понял, повторите...", recognizer.default_lang))
#                     logger.info("🤔 Не понял, повторите...")
#                     miss_count = 0
#                 time.sleep(0.05)
#         except Exception as e:
#             logger.error(f"[Recognizer ERROR] {e}")
#             time.sleep(0.5)

# # === Вспомогательные функции ===
# def clean_text(text: str, wake_word: str = None) -> str:
#     """Удаляет wake word из текста"""
#     if not text:
#         return ""
#     if wake_word:
#         text = re.sub(rf"\b{re.escape(wake_word)}\b", "", text, flags=re.IGNORECASE)
#     return text.strip().lower()


# def is_reload_command(text: str, meta: dict, key: str) -> bool:
#     """Проверяет, является ли команда командой перезагрузки"""
#     if not text or not meta:
#         return False
#     patterns = meta.get(key, {}).get("patterns", [])
#     return any(text == p.lower() for p in patterns)


# def build_wake_words(config: dict) -> set:
#     """Извлекает все слова активации из конфигурации"""
#     wake_words = set()

#     for lang, words in (config.get("wake_words") or {}).items():
#         if isinstance(words, list):
#             wake_words.update(map(str.lower, words))

#     # добавляем старое поле для совместимости
#     single_word = config.get("wake_word")
#     if single_word:
#         wake_words.add(single_word.lower())

#     return wake_words


# # === Основная логика ассистента ===
# def process_text(executor: Executor, dataset: dict, skills: SkillManager,
#                  text: str, lang: str, wake_words: set,
#                  active_state: dict):
#     """Главная функция обработки текста"""

#     normalized = text.lower().strip()
#     lang = lang or "ru"
#     logger.info(f"🧠 Распознано ({lang}): {normalized}")

#     # === Обработка Wake Word ===
#     if not active_state["active"]:
#         triggered = next((w for w in wake_words if re.search(rf"\b{re.escape(w)}\b", normalized)), None)

#         if triggered:
#             cleaned = clean_text(normalized, triggered)
#             active_state["active"] = True
#             active_state["last"] = time.time()

#             if not cleaned:
#                 logger.info(f"🚀 Активирован wake word: '{triggered}'")
#                 tts_queue.put(("Слушаю вас.", lang))
#                 return

#             logger.info(f"🚀 Wake word '{triggered}', сразу выполняю команду: {cleaned}")
#             response = executor.handle(cleaned, lang=lang)
#             if response:
#                 tts_queue.put((response, lang))
#             return
#         return  # не активирован — ждём wake word

#     # === Проверка тайм-аута активности ===
#     if time.time() - active_state["last"] > active_state["timeout"]:
#         logger.info("😴 Время активности истекло.")
#         active_state["active"] = False
#         return

#     # === Обработка команд ===
#     triggered = next((w for w in wake_words if w in normalized), None)
#     cleaned_text = clean_text(normalized, triggered)
#     if not cleaned_text:
#         tts_queue.put(("Да, я слушаю.", lang))
#         return

#     meta = dataset.get("meta", {}) or {}

#     # === Системные команды ===
#     if is_reload_command(cleaned_text, meta, "reload_dataset"):
#         logger.info("🔁 Перезагрузка датасета...")
#         new_settings = get_settings()
#         dataset = new_settings.dataset
#         executor.update_dataset(dataset)
#         skills.reload()
#         msg = meta.get("reload_dataset", {}).get("response", {}).get(lang, "Данные обновлены.")
#         tts_queue.put((msg, lang))
#         return

#     if is_reload_command(cleaned_text, meta, "restart_skills"):
#         logger.info("🔁 Перезапуск навыков...")
#         skills.reload()
#         msg = meta.get("restart_skills", {}).get("response", {}).get(lang, "Навыки перезапущены.")
#         tts_queue.put((msg, lang))
#         return

#     # === Выполнение команды пользователя ===
#     response = executor.handle(cleaned_text, lang=lang)
#     if response:
#         tts_queue.put((response, lang))
#         active_state["last"] = time.time()
#     else:
#         tts_queue.put(("Не понял, повторите.", lang))


# # === Главная функция запуска ===
# def main():
#     settings = get_settings()
#     config = settings.config
#     dataset = settings.dataset

#     recognizer = Recognizer(config)
#     tts = HybridTTS(config)

#     context = {"config": config, "dataset": dataset, "workers": WORKERS, "tts": tts}
#     skills = SkillManager(context=context)
#     executor = Executor(dataset, skills, config=config)

#     wake_words = build_wake_words(config)
#     logger.info(f"🎧 Слова активации: {', '.join(wake_words)}")

#     # === Запуск потоков ===
#     threading.Thread(target=tts_worker, args=(tts,), daemon=True).start()
#     threading.Thread(target=recognizer_worker, args=(recognizer,), daemon=True).start()

#     active_state = {"active": False, "last": 0.0, "timeout": 20.0}
#     logger.info("🤖 Jarvis запущен и слушает...")

#     while True:
#         try:
#             text, lang = recognizer_queue.get(timeout=0.1)
#             if text:
#                 process_text(executor, dataset, skills, text, lang, wake_words, active_state)
#         except queue.Empty:
#             continue
#         except KeyboardInterrupt:
#             logger.info("🛑 Завершение работы по Ctrl+C")
#             break
#         except Exception as e:
#             logger.error(f"[MAIN ERROR] {e}")
#             time.sleep(0.3)


# if __name__ == "__main__":
#     main()
