from src.core.config_loader import load_config
from src.core.dataset_loader import load_dataset
from src.core.recognizer import Recognizer
from src.core.tts import HybridTTS
from src.core.skill_manager import SkillManager
from src.core.executor import Executor
import time
import re
import traceback
import speech_recognition as sr  # для перехвата WaitTimeoutError


def clean_text(text: str, wake_word: str) -> str:
    """Удаляет слово активации из команды."""
    if not text:
        return ""
    pattern = r"(^|\b)" + re.escape(wake_word) + r"(\b|$)"
    return re.sub(pattern, "", text.lower(), flags=re.IGNORECASE).strip()


def is_reload_command(text: str, meta: dict, key: str) -> bool:
    """Проверяет, является ли команда служебной."""
    if not text or not meta:
        return False
    patterns = meta.get(key, {}).get("patterns", [])
    return any(text == p.lower() for p in patterns)


def main():
    # === Инициализация ===
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

    print(f"🎧 Voice Assistant is ready! Say '{wake_word.title()}' to activate.\n")

    while True:
        try:
            try:
                result = recognizer.listen_text(multilang=True)
            except sr.WaitTimeoutError:
                # Просто пропускаем, если никто не говорит
                continue

            if not result:
                continue

            text, lang = (result if isinstance(result, tuple)
                          else (result, config.get("assistant", {}).get("default_language", "ru")))

            normalized = text.lower().strip()
            print(f"🧠 You said ({lang}): {text}")

            # === 1. Проверяем слово активации ===
            if not active_mode:
                if wake_word in normalized:
                    active_mode = True
                    last_activation = time.time()
                    print("🚀 Wake word detected! Assistant activated.")
                    tts.speak("Слушаю вас.", lang=lang)

                    cleaned = clean_text(normalized, wake_word)
                    if cleaned:
                        response = executor.handle(cleaned, lang=lang)
                        print(f"🤖 Assistant: {response}")
                        tts.speak(response, lang=lang)
                    continue
                else:
                    continue

            # === 2. Проверяем таймер активности ===
            if time.time() - last_activation > active_duration:
                print("😴 Время активации истекло. Ожидаю слово пробуждения...")
                active_mode = False
                continue

            # === 3. Удаляем слово активации ===
            cleaned_text = clean_text(normalized, wake_word)
            if not cleaned_text:
                tts.speak("Да, я вас слушаю.", lang=lang)
                continue

            # === 4. Горячие команды ===
            meta = dataset.get("meta", {}) or {}

            if is_reload_command(cleaned_text, meta, "reload_dataset"):
                dataset = load_dataset("data/commands.yaml")
                executor.update_dataset(dataset)
                skills.reload()
                msg = meta.get("reload_dataset", {}).get("response", {}).get(lang, "Данные обновлены.")
                print(msg)
                tts.speak(msg, lang=lang)
                continue

            if is_reload_command(cleaned_text, meta, "restart_skills"):
                skills.reload()
                msg = meta.get("restart_skills", {}).get("response", {}).get(lang, "Навыки перезапущены.")
                print(msg)
                tts.speak(msg, lang=lang)
                continue

            # === 5. Основная команда ===
            response = executor.handle(cleaned_text, lang=lang)
            if response:
                print(f"🤖 Assistant: {response}")
                tts.speak(response, lang=lang)
            else:
                tts.speak("Не понял, повторите.", lang=lang)

        except KeyboardInterrupt:
            print("\n🛑 Exiting...")
            break

        except Exception as e:
            # Перехватываем все непредвиденные ошибки
            print(f"[ERROR main] {e}")
            print(traceback.format_exc())
            # Не проговариваем TTS при тихих сбоях
            time.sleep(0.3)
            continue


if __name__ == "__main__":
    main()
