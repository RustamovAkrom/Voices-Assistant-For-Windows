from src.core.recognizer import Recognizer
from src.core.executor import Executor
from src.core.tts import TTS
from src.core.config_loader import load_config
from src.core.dataset_loader import load_dataset
from src.core.skill_manager import SkillManager

def main():
    config = load_config("data/config.yaml")
    dataset = load_dataset("data/commands.yaml")

    recognizer = Recognizer(config)
    tts = TTS(config)
    skills = SkillManager()
    executor = Executor(dataset, skills)

    print("🎧 Voice Assistant is ready! Say something...")

    while True:
        text = recognizer.listen_text()  # Пока только текст, потом подключим голос
        if not text:
            continue

        print(f"🧠 You said: {text}")
        response = executor.handle(text)

        print(f"🤖 Assistant: {response}")
        tts.speak(response)


if __name__ == "__main__":
    main()
