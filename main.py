import time
import re
import threading
import queue
import speech_recognition as sr
import logging
from pathlib import Path

from src.core.recognizer import Recognizer
from src.core.tts import HybridTTS
from src.core.skill_manager import SkillManager
from src.core.executor import Executor
from src.core.config import get_settings

# ===== Настройка логирования =====
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("Assistant")

tts_queue = queue.Queue()
recognizer_queue = queue.Queue()

def tts_worker(tts: HybridTTS):
    while True:
        text, lang = tts_queue.get()
        try:
            if text:
                tts.speak(text, lang)
        except Exception as e:
            logger.error(f"[TTS ERROR] {e}")
        finally:
            tts_queue.task_done()

def listen_loop(recognizer: Recognizer):
    while True:
        try:
            result = recognizer.listen_text(multilang=True)
            if result:
                recognizer_queue.put(result)
        except Exception as e:
            logger.error(f"[Recognizer ERROR] {e}")
            time.sleep(0.5)

def clean_text(text: str, wake_word: str) -> str:
    """Удаляем слово активации из текста (целиком)."""
    if not text: return ""
    pattern = r"(^|\b)" + re.escape(wake_word) + r"(\b|$)"
    return re.sub(pattern, "", text.lower(), flags=re.IGNORECASE).strip()

def is_reload_command(text: str, meta: dict, key: str) -> bool:
    if not text or not meta: return False
    patterns = meta.get(key, {}).get("patterns", [])
    return any(text == p.lower() for p in patterns)

def main():
    settings = get_settings()
    config = settings.config
    dataset = settings.dataset

    recognizer = Recognizer(config)
    tts = HybridTTS(config)
    skills = SkillManager(debug=config.get("debug", False))
    executor = Executor(dataset, skills, config=config)

    # Если есть приветственный аудио-файл, проигрываем его
    try:
        greet_path = Path("data/media/audios/greeting.wav")
        if greet_path.exists():
            tts.play_audio_file(greet_path)
    except Exception:
        pass

    wake_word = config.get("wake_word", "джарвис").lower().strip()
    active_mode = False
    last_activation = 0
    active_duration = 15  # секунд

    threading.Thread(target=tts_worker, args=(tts,), daemon=True).start()
    threading.Thread(target=listen_loop, args=(recognizer,), daemon=True).start()

    logger.info(f"🎧 Ассистент готов! Слово активации: '{wake_word}'.\n")
    while True:
        try:
            try:
                result = recognizer_queue.get_nowait()
            except queue.Empty:
                time.sleep(0.1)
                continue

            if not result:
                continue
            text, lang = result
            normalized = text.lower().strip()
            logger.info(f"🧠 Сказано ({lang}): {text}")

            # Если режим ожидания
            if not active_mode:
                if wake_word in normalized:
                    active_mode = True
                    last_activation = time.time()
                    logger.info("🚀 Ассистент активирован.")
                    # Говорим ответ подтверждения
                    tts_queue.put(("Слушаю вас.", lang))
                    # Если после слова активации есть команда, обрабатываем её
                    cleaned = clean_text(normalized, wake_word)
                    if cleaned:
                        response = executor.handle(cleaned, lang=lang)
                        if response:
                            logger.info(f"🤖 Ассистент: {response}")
                            tts_queue.put((response, lang))
                    continue
                else:
                    continue

            # Проверка тайм-аута активности
            if time.time() - last_activation > active_duration:
                logger.info("😴 Время активности истекло. Ждём повторного вызова.")
                active_mode = False
                continue

            # Основная команда (удаляем wake-word, если сказано)
            cleaned_text = clean_text(normalized, wake_word)
            if not cleaned_text:
                tts_queue.put(("Да, я слушаю.", lang))
                continue

            meta = dataset.get("meta", {}) or {}

            # Команда обновления датасета
            if is_reload_command(cleaned_text, meta, "reload_dataset"):
                settings = get_settings()  # перечитываем конфиг и датасет
                dataset = settings.dataset
                executor.update_dataset(dataset)
                skills.reload()
                msg = meta.get("reload_dataset", {}).get("response", {}).get(lang, "Данные обновлены.")
                logger.info(msg)
                tts_queue.put((msg, lang))
                continue

            # Команда перезагрузки навыков
            if is_reload_command(cleaned_text, meta, "restart_skills"):
                skills.reload()
                msg = meta.get("restart_skills", {}).get("response", {}).get(lang, "Навыки перезапущены.")
                logger.info(msg)
                tts_queue.put((msg, lang))
                continue

            # Выполнение основной команды
            response = executor.handle(cleaned_text, lang=lang)
            if response:
                logger.info(f"🤖 Ассистент: {response}")
                tts_queue.put((response, lang))
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
