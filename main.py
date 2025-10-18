from src.core.config_loader import load_config
from src.core.dataset_loader import load_dataset
from src.core.recognizer import Recognizer
from src.core.tts import HybridTTS
from src.core.skill_manager import SkillManager
from src.core.executor import Executor
import time

def main():
    config = load_config("data/config.yaml")
    dataset = load_dataset("data/commands.yaml")

    recognizer = Recognizer(config)
    tts = HybridTTS(config)
    skills = SkillManager(debug=config.get("debug", False))
    executor = Executor(dataset, skills, config=config)

    print("🎧 Voice Assistant is ready! Say something (RU / EN / UZ)...")

    while True:
        try:
            res = recognizer.listen_text(multilang=True)
            if not res:
                continue
            # res is (text, lang)
            if isinstance(res, tuple):
                text, lang = res
            else:
                text, lang = res, config.get("language_default", "ru")

            print(f"🧠 You said ({lang}): {text}")

            # hot-commands handling before main executor: reload dataset/skills
            low = text.lower()
            # check meta hot commands from dataset
            meta = dataset.get("meta", {}) or {}
            reload_phrases = meta.get("reload_dataset", {}).get("patterns", [])
            reload_skills_phrases = meta.get("restart_skills", {}).get("patterns", [])
            
            if any(p.lower() == low for p in reload_phrases):
                dataset = load_dataset("data/commands.yaml")
                executor.update_dataset(dataset)
                skills.reload()
                msg = meta.get("reload_dataset", {}).get("response", {}).get(lang, "Dataset reloaded.")
                print(msg)
                tts.speak(msg, lang=lang)
                continue

            if any(p.lower() == low for p in reload_skills_phrases):
                skills.reload()
                msg = meta.get("restart_skills", {}).get("response", {}).get(lang, "Skills reloaded.")
                print(msg)
                tts.speak(msg, lang=lang)
                continue

            # main handling
            response = executor.handle(text, lang=lang)
            print(f"🤖 Assistant: {response}")
            tts.speak(response, lang=lang)

        except KeyboardInterrupt:
            print("\n🛑 Exiting...")
            break
        except Exception as e:
            print(f"[ERROR main] {e}")
            tts.speak("Произошла ошибка, пробую продолжить работу.")
            time.sleep(0.5)

if __name__ == "__main__":
    main()
