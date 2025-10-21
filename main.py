from src.core.config_loader import load_config
from src.core.dataset_loader import load_dataset
from src.core.recognizer import Recognizer
from src.core.tts import HybridTTS
from src.core.skill_manager import SkillManager
from src.core.executor import Executor
import time
import re
import traceback
import speech_recognition as sr
import threading
import queue

# ===== Очереди =====
tts_queue = queue.Queue()
recognizer_queue = queue.Queue()

# ===== Поток TTS =====
def tts_worker(tts):
    while True:
        text, lang = tts_queue.get()
        try:
            tts.speak(text, lang=lang)
        except Exception as e:
            print(f"[TTS ERROR] {e}")
        tts_queue.task_done()

# ===== Поток прослушивания =====
def listen_loop(recognizer):
    while True:
        try:
            result = recognizer.listen_text(multilang=True)
            if result:
                recognizer_queue.put(result)
        except sr.WaitTimeoutError:
            continue
        except Exception as e:
            print(f"[Recognizer ERROR] {e}")

# ===== Функции =====
def clean_text(text: str, wake_word: str) -> str:
    if not text:
        return ""
    pattern = r"(^|\b)" + re.escape(wake_word) + r"(\b|$)"
    return re.sub(pattern, "", text.lower(), flags=re.IGNORECASE).strip()

def is_reload_command(text: str, meta: dict, key: str) -> bool:
    if not text or not meta:
        return False
    patterns = meta.get(key, {}).get("patterns", [])
    return any(text == p.lower() for p in patterns)

def main():
    config = load_config("data/config.yaml")
    dataset = load_dataset("data/commands.yaml")

    recognizer = Recognizer(config)
    tts = HybridTTS(config)
    skills = SkillManager(debug=config.get("debug", False))
    executor = Executor(dataset, skills, config=config)

    wake_word = config.get("wake_word", "джарвис").lower().strip()
    active_mode = False
    last_activation = 0
    active_duration = 15  # секунд

    # ===== Старт потоков =====
    threading.Thread(target=tts_worker, args=(tts,), daemon=True).start()
    threading.Thread(target=listen_loop, args=(recognizer,), daemon=True).start()

    print(f"🎧 Voice Assistant is ready! Say '{wake_word.title()}' to activate.\n")

    while True:
        try:
            # ===== Получаем результат из очереди =====
            try:
                result = recognizer_queue.get_nowait()
            except queue.Empty:
                time.sleep(0.1)
                continue

            if not result:
                continue

            text, lang = (result if isinstance(result, tuple)
                          else (result, config.get("assistant", {}).get("default_language", "ru")))
            normalized = text.lower().strip()
            print(f"🧠 You said ({lang}): {text}")

            # ===== 1. Слово активации =====
            if not active_mode:
                if wake_word in normalized:
                    active_mode = True
                    last_activation = time.time()
                    print("🚀 Wake word detected! Assistant activated.")
                    tts_queue.put(("Слушаю вас.", lang))

                    cleaned = clean_text(normalized, wake_word)
                    if cleaned:
                        response = executor.handle(cleaned, lang=lang)
                        print(f"🤖 Assistant: {response}")
                        tts_queue.put((response, lang))
                    continue
                else:
                    continue

            # ===== 2. Таймер активности =====
            if time.time() - last_activation > active_duration:
                print("😴 Время активации истекло. Ожидаю слово пробуждения...")
                active_mode = False
                continue

            # ===== 3. Основные команды =====
            cleaned_text = clean_text(normalized, wake_word)
            if not cleaned_text:
                tts_queue.put(("Да, я вас слушаю.", lang))
                continue

            meta = dataset.get("meta", {}) or {}

            if is_reload_command(cleaned_text, meta, "reload_dataset"):
                dataset = load_dataset("data/commands.yaml")
                executor.update_dataset(dataset)
                skills.reload()
                msg = meta.get("reload_dataset", {}).get("response", {}).get(lang, "Данные обновлены.")
                print(msg)
                tts_queue.put((msg, lang))
                continue

            if is_reload_command(cleaned_text, meta, "restart_skills"):
                skills.reload()
                msg = meta.get("restart_skills", {}).get("response", {}).get(lang, "Навыки перезапущены.")
                print(msg)
                tts_queue.put((msg, lang))
                continue

            # ===== 4. Основная команда =====
            response = executor.handle(cleaned_text, lang=lang)
            if response:
                print(f"🤖 Assistant: {response}")
                tts_queue.put((response, lang))
            else:
                tts_queue.put(("Не понял, повторите.", lang))

        except KeyboardInterrupt:
            print("\n🛑 Exiting...")
            break
        except Exception as e:
            print(f"[ERROR main] {e}")
            print(traceback.format_exc())
            time.sleep(0.3)
            continue

if __name__ == "__main__":
    main()
