import time
import re
import threading
import queue
import logging


from src.core.recognizer import Recognizer
from src.core.tts import HybridTTS
from src.core.skill_manager import SkillManager
from src.core.executor import Executor
from src.core.config import get_settings

# === Логирование ===
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("Assistant")

WORKERS = []
tts_queue = queue.Queue()
recognizer_queue = queue.Queue()


# === Поток TTS ===
def tts_worker(tts: HybridTTS):
    while True:
        text, lang = tts_queue.get()
        if not text:
            continue
        try:
            if text:
                tts.speak(text, lang)
        except Exception as e:
            logger.error(f"[TTS ERROR] {e}")
        finally:
            tts_queue.task_done()


# === Поток прослушивания ===
def recognizer_worker(recognizer: Recognizer, silence_threshold=3.0):
    """
    Постоянно слушает микрофон.
    Если пользователь делает паузу > silence_threshold секунд — считаем, что он закончил говорить.
    """
    last_speech_time = 0
    buffer_text = ""

    while True:
        try:
            result = recognizer.listen_text()
            if result:
                text, lang = result
                buffer_text = text
                last_speech_time = time.time()

                # Если пользователь всё ещё говорит — ждём окончания
                recognizer_queue.put((buffer_text.strip(), lang))

            else:
                # Проверяем, не истекла ли пауза
                if time.time() - last_speech_time >= silence_threshold and buffer_text:
                    # Отправляем накопленный текст на обработку
                    recognizer_queue.put((buffer_text.strip(), None))
                    buffer_text = ""

                time.sleep(0.2)

        except Exception as e:
            logger.error(f"[Recognizer ERROR] {e}")
            time.sleep(0.5)


# === Удаляем wake word из текста ===
def clean_text(text: str, wake_word: str) -> str:
    if not text:
        return ""
    pattern = r"(^|\b)" + re.escape(wake_word) + r"(\b|$)"
    return re.sub(pattern, "", text.lower(), flags=re.IGNORECASE).strip()


# === Проверяем команды перезагрузки ===
def is_reload_command(text: str, meta: dict, key: str) -> bool:
    if not text or not meta:
        return False
    patterns = meta.get(key, {}).get("patterns", [])
    return any(text == p.lower() for p in patterns)


# === Основная функция ===
def main():
    settings = get_settings()
    config = settings.config
    dataset = settings.dataset
    context = {
        "config": config,
        "dataset": dataset,
        "workers": WORKERS
    }
    recognizer = Recognizer(config)
    tts = HybridTTS(config)
    skills = SkillManager(context=context)
    executor = Executor(dataset, skills, config=config)

    # === Настройка wake words ===
    wake_words_config = config.get("wake_words", {})
    wake_words = set()

    if isinstance(wake_words_config, dict):
        for lang, words in wake_words_config.items():
            if isinstance(words, list):
                wake_words.update(w.lower().strip() for w in words)

    # добавляем старый wake_word для совместимости
    single_word = config.get("wake_word", "")
    if single_word:
        wake_words.add(single_word.lower().strip())

    logger.info(f"🎧 Слова активации: {', '.join(wake_words)}")

    # === Состояния ===
    active_mode = False
    last_activation = 0
    active_duration = 20  # больше времени, чтобы не спешить

    thread1 = threading.Thread(target=tts_worker, args=(tts,), daemon=True)
    thread2 = threading.Thread(target=recognizer_worker, args=(recognizer,), daemon=True)
    thread1.start()
    thread2.start()
    
    WORKERS.extend([thread1, thread2])

    logger.info("🤖 Jarvis запущен и слушает...")

    while True:
        try:
            try:
                result = recognizer_queue.get(timeout=0.1)
            except queue.Empty:
                time.sleep(0.1)
                continue

            if not result:
                continue

            text, lang = result
            if not text:
                continue
            
            normalized = text.lower().strip()
            
            lang = lang or "ru"
            logger.info(f"🧠 Распознано ({lang}): {normalized}")

            # === Проверяем wake word ===
            if not active_mode:
                triggered = next((w for w in wake_words if w in normalized), None)
                if triggered:
                    active_mode = True
                    last_activation = time.time()
                    logger.info(f"🚀 Активирован wake word: '{triggered}'")
                    tts_queue.put(("Слушаю вас.", lang))
                    cleaned = clean_text(normalized, triggered)
                    if cleaned:
                        response = executor.handle(cleaned, lang=lang)
                        if response:
                            logger.info(f"🤖 Jarvis: {response}")
                            tts_queue.put((response, lang))
                    continue
                else:
                    continue

            # === Проверка тайм-аута активности ===
            if time.time() - last_activation > active_duration:
                logger.info("😴 Время активности истекло. Ожидание нового вызова.")
                active_mode = False
                continue

            # === Обработка команды ===
            triggered_word = next((w for w in wake_words if w in normalized), None)
            cleaned_text = clean_text(normalized, triggered_word) if triggered_word else normalized
            meta = dataset.get("meta", {}) or {}

            if not cleaned_text:
                tts_queue.put(("Да, я слушаю.", lang))
                continue

            # === Проверяем специальные команды ===
            if is_reload_command(cleaned_text, meta, "reload_dataset"):
                settings = get_settings()
                dataset = settings.dataset
                executor.update_dataset(dataset)
                skills.reload()
                msg = meta.get("reload_dataset", {}).get("response", {}).get(lang, "Данные обновлены.")
                logger.info(msg)
                tts_queue.put((msg, lang))
                continue

            if is_reload_command(cleaned_text, meta, "restart_skills"):
                skills.reload()
                msg = meta.get("restart_skills", {}).get("response", {}).get(lang, "Навыки перезапущены.")
                logger.info(msg)
                tts_queue.put((msg, lang))
                continue

            # === Выполнение обычных команд ===
            response = executor.handle(cleaned_text, lang=lang)
            if response:
                logger.info(f"🤖 Jarvis: {response}")
                tts_queue.put((response, lang))
                last_activation = time.time()
                active_duration = 20
                print(f"⏱️ Активное время продлено на 20 сек (итого {active_duration})")
            else:
                tts_queue.put(("Не понял, повторите.", lang))

        except KeyboardInterrupt:
            logger.info("\n🛑 Завершение работы...")
            break
        
        except Exception as e:
            logger.error(f"[MAIN ERROR] {e}")
            time.sleep(0.3)
            continue


if __name__ == "__main__":
    main()
