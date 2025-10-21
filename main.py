import time
import re
import traceback
import threading
import queue
import speech_recognition as sr
import logging

from src.core.recognizer import Recognizer
from src.core.tts import HybridTTS
from src.core.skill_manager import SkillManager
from src.core.executor import Executor
from src.core.config import get_settings


# ===== Настройка логгирования =====
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("Jarvis")


# ===== Очереди =====
tts_queue = queue.Queue()
recognizer_queue = queue.Queue()


# ===== Поток TTS =====
def tts_worker(tts: HybridTTS):
    while True:
        text, lang = tts_queue.get()
        try:
            if text:
                tts.speak(text, lang=lang)
        except Exception as e:
            logger.error(f"[TTS ERROR] {e}")
        finally:
            tts_queue.task_done()


# ===== Поток прослушивания =====
def listen_loop(recognizer: Recognizer):
    while True:
        try:
            result = recognizer.listen_text(multilang=True)
            if result:
                recognizer_queue.put(result)
        except sr.WaitTimeoutError:
            continue
        except Exception as e:
            logger.error(f"[Recognizer ERROR] {e}")
            time.sleep(0.5)  # маленькая пауза чтобы избежать зацикливания


# ===== Вспомогательные функции =====
def clean_text(text: str, wake_word: str) -> str:
    """Удаляет слово активации из текста."""
    if not text:
        return ""
    pattern = r"(^|\b)" + re.escape(wake_word) + r"(\b|$)"
    return re.sub(pattern, "", text.lower(), flags=re.IGNORECASE).strip()


def is_reload_command(text: str, meta: dict, key: str) -> bool:
    """Проверяет, совпадает ли текст с паттернами команды перезагрузки."""
    if not text or not meta:
        return False
    patterns = meta.get(key, {}).get("patterns", [])
    return any(text == p.lower() for p in patterns)


# ===== Главная функция =====
def main():
    # === Загрузка настроек и данных ===
    settings = get_settings()
    config = settings.config
    dataset = settings.dataset

    recognizer = Recognizer(config)
    tts = HybridTTS(config)
    skills = SkillManager(debug=config.get("debug", False))
    executor = Executor(dataset, skills, config=config)

    wake_word = config.get("wake_word", "джарвис").lower().strip()
    active_mode = False
    last_activation = 0
    active_duration = 15  # секунд

    # === Запуск потоков ===
    threading.Thread(target=tts_worker, args=(tts,), daemon=True).start()
    threading.Thread(target=listen_loop, args=(recognizer,), daemon=True).start()

    logger.info(f"🎧 Voice Assistant is ready! Say '{wake_word.title()}' to activate.\n")

    while True:
        try:
            # Получаем распознанную фразу
            try:
                result = recognizer_queue.get_nowait()
            except queue.Empty:
                time.sleep(0.1)
                continue

            if not result:
                continue

            text, lang = (
                result if isinstance(result, tuple)
                else (result, config.get("language_default", "ru"))
            )
            normalized = text.lower().strip()
            logger.info(f"🧠 You said ({lang}): {text}")

            # === 1. Слово активации ===
            if not active_mode:
                if wake_word in normalized:
                    active_mode = True
                    last_activation = time.time()
                    logger.info("🚀 Wake word detected! Assistant activated.")
                    tts_queue.put(("Слушаю вас.", lang))

                    cleaned = clean_text(normalized, wake_word)
                    if cleaned:
                        response = executor.handle(cleaned, lang=lang)
                        if response:
                            logger.info(f"🤖 Assistant: {response}")
                            tts_queue.put((response, lang))
                    continue
                else:
                    continue

            # === 2. Проверка таймера активности ===
            if time.time() - last_activation > active_duration:
                logger.info("😴 Время активации истекло. Ожидаю слово пробуждения...")
                active_mode = False
                continue

            # === 3. Основные команды ===
            cleaned_text = clean_text(normalized, wake_word)
            if not cleaned_text:
                tts_queue.put(("Да, я вас слушаю.", lang))
                continue

            meta = dataset.get("meta", {}) or {}

            # Перезагрузка датасета (через Settings)
            if is_reload_command(cleaned_text, meta, "reload_dataset"):
                settings = get_settings()  # пересоздаём объект (с кешем)
                dataset = settings.dataset
                executor.update_dataset(dataset)
                skills.reload()
                msg = meta.get("reload_dataset", {}).get("response", {}).get(lang, "Данные обновлены.")
                logger.info(msg)
                tts_queue.put((msg, lang))
                continue

            # Перезапуск навыков
            if is_reload_command(cleaned_text, meta, "restart_skills"):
                skills.reload()
                msg = meta.get("restart_skills", {}).get("response", {}).get(lang, "Навыки перезапущены.")
                logger.info(msg)
                tts_queue.put((msg, lang))
                continue

            # === 4. Выполнение основной команды ===
            response = executor.handle(cleaned_text, lang=lang)
            if response:
                logger.info(f"🤖 Assistant: {response}")
                tts_queue.put((response, lang))
            else:
                tts_queue.put(("Не понял, повторите.", lang))

        except KeyboardInterrupt:
            logger.info("\n🛑 Exiting...")
            break
        except Exception as e:
            logger.error(f"[MAIN ERROR] {e}")
            logger.debug(traceback.format_exc())
            time.sleep(0.3)
            continue


if __name__ == "__main__":
    main()
