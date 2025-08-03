import pyttsx3


class Speaker:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 150)  # Скорость речи
        self._set_voice()

    def _set_voice(self):
        # Получаем доступные голоса
        voices = self.engine.getProperty("voices")
        for voice in voices:
            print(f"Voice: {voice.name} - ID: {voice.id} - Lang: {voice.languages}")

        # Выбираем голос по нужному имени или языку
        for voice in voices:
            if "russian" in voice.name.lower() or "русский" in voice.name.lower():
                self.engine.setProperty("voice", voice.id)
                break

    def say(self, text):
        self.engine.say(text)
        self.engine.runAndWait()
