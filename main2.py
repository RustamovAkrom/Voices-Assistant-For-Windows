import threading
import time
import logging
from src.core.porcupine_listener import PorcupineListener
from src.core.recognizer import Recognizer
from src.core.tts import HybridTTS
from src.core.skill_manager import SkillManager
from src.core.executor import Executor
from src.core.config import get_settings

logger = logging.getLogger("Jarvis")

class JarvisAssistant:
    def __init__(self):
        settings = get_settings()
        self.config = settings.config
        self.dataset = settings.dataset

        self.recognizer = Recognizer(self.config)
        self.tts = HybridTTS(self.config)
        self.skills = SkillManager(context={
            "config": self.config, 
            "dataset": self.dataset, 
            "tts": self.tts
        })
        self.executor = Executor(self.dataset, self.skills, config=self.config)
        self.porcupine = PorcupineListener(keyword="jarvis", sensitivity=0.7)

        self.active = False
        self.last_heard = 0
        self.active_timeout = 20  # 20 сек бездействия
        self.listening_thread = threading.Thread(target=self.passive_listen, daemon=True)

    def say(self, text):
        """Говорим, но не блокируем микрофон"""
        threading.Thread(target=lambda: self.tts.speak(text, "ru"), daemon=True).start()

    def passive_listen(self):
        """Фоновое прослушивание wake word"""
        while True:
            if self.porcupine.listen():
                self.activate()

    def activate(self):
        """Активируем ассистента после wake word"""
        if self.active:
            return
        self.active = True
        self.last_heard = time.time()
        self.say("Да, сэр!")
        logger.info("🎤 Активирован Jarvis")

        threading.Thread(target=self.active_listen, daemon=True).start()

    def active_listen(self):
        """Активное слушание команд после активации"""
        while self.active:
            if time.time() - self.last_heard > self.active_timeout:
                logger.info("😴 Время активности истекло, Jarvis засыпает.")
                self.active = False
                break

            text_result = self.recognizer.listen_text()

            if not text_result:
                continue

            text, lang = text_result
            text = text.strip()
            logger.info(f"🧠 Распознано: {text}")

            self.last_heard = time.time()  # обновляем таймер при каждой фразе
            response = self.executor.handle(text.lower(), lang=lang)

            if response:
                self.say(response)
            else:
                self.say("Не понял, повторите, сэр.")

    def run(self):
        self.listening_thread.start()
        logger.info("🤖 Jarvis слушает wake word (Porcupine активен).")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Завершение работы Jarvis.")
            self.porcupine.stop()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, 
        format="[%(asctime)s] [%(levelname)s] %(message)s", 
        datefmt="%H:%M:%S"
    )
    jarvis = JarvisAssistant()
    jarvis.run()
