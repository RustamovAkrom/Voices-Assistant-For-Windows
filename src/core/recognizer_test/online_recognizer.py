import io
import sounddevice as sd
import speech_recognition as sr
from scipy.io.wavfile import write as wav_write
import requests


class OnlineRecognizer:
    def __init__(self, config, audio_queue):
        self.config = config
        self.audio_queue = audio_queue
        self.language_map = {"ru": "ru-RU", "en": "en-US", "uz": "uz-UZ"}
        self.default_lang = config.get("assistant", {}).get("default_language", "ru")

    def _check_internet(self):
        try:
            requests.get("https://www.google.com", timeout=3)
            return True
        except requests.RequestException:
            raise ConnectionError("Нет соединения с интернетом.")

    def listen_text(self):
        self._check_internet()
        print("🎙️ (ONLINE) Слушаю...")

        samplerate = 16000
        duration = 4
        with sd.InputStream(samplerate=samplerate, channels=1, dtype="int16") as stream:
            audio_data = stream.read(int(samplerate * duration))[0]

        wav_bytes = io.BytesIO()
        wav_write(wav_bytes, samplerate, audio_data)
        wav_bytes.seek(0)

        r = sr.Recognizer()
        with sr.AudioFile(wav_bytes) as source:
            audio = r.record(source)

        lang_code = self.language_map.get(self.default_lang, "ru-RU")
        text = r.recognize_google(audio, language=lang_code)
        print(f"🧠 Распознано ({self.default_lang.upper()}): {text}")
        return text, self.default_lang
