import os
import sys
import json
import queue
import zipfile
import urllib.request
from io import BytesIO
from pathlib import Path
import sounddevice as sd
import speech_recognition as sr
from vosk import Model, KaldiRecognizer, SetLogLevel
from langdetect import detect, DetectorFactory

from src.core.config import MODELS_DIR, VOSK_MODEL_URLS, DETECT_LANGUAGE_WORDS, get_settings
from src.utils.base import check_internet

# Фиксируем seed для детерминированности langdetect:contentReference[oaicite:3]{index=3}
DetectorFactory.seed = 0

class Recognizer:
    def __init__(self, config):
        self.config = config
        self.default_lang = config.get("assistant", {}).get("default_language", "ru")
        self.models_dir = MODELS_DIR
        self.models_dir.mkdir(parents=True, exist_ok=True)

        self.vosk_models = {
            "ru": self.models_dir / "vosk-model-small-ru-0.22",
            "en": self.models_dir / "vosk-model-small-en-us-0.15",
            "uz": self.models_dir / "vosk-model-small-uz-0.22",
        }

        SetLogLevel(-1)
        self.online_available = check_internet()

        # Если режим офлайн по настройке, сразу переходим в офлайн
        if self.config.get("offline_mode", False):
            self.online_available = False
        # Обеспечение наличия моделей VOSK
        self._ensure_vosk_models()
        self.vosk_recognizers = self._load_vosk_recognizers()

        if self.online_available:
            self._init_online_recognition()
        else:
            self._init_offline_recognition()

    def _init_online_recognition(self):
        self.mode = "online"
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        print("🌐 Режим распознавания: ONLINE")

    def _init_offline_recognition(self):
        self.mode = "offline"
        print("⚙️ Режим распознавания: OFFLINE")

    def _ensure_vosk_models(self):
        for lang, path in self.vosk_models.items():
            if not path.exists():
                if self.online_available:
                    print(f"📦 Скачиваю модель VOSK для {lang.upper()}...")
                    try:
                        self._download_and_extract(VOSK_MODEL_URLS[lang], self.models_dir)
                        print(f"✅ Модель установлена: {path.name}")
                    except Exception as e:
                        print(f"❌ Ошибка при скачивании модели {lang}: {e}")
                        if not self.config.get("offline_mode", False):
                            sys.exit(1)
                else:
                    print(f"❌ Модель для {lang.upper()} не найдена и нет интернета.")
                    sys.exit(1)

    def _download_and_extract(self, url, target_dir):
        with urllib.request.urlopen(url) as resp:
            with zipfile.ZipFile(BytesIO(resp.read())) as zf:
                zf.extractall(self.models_dir)

    def _load_vosk_recognizers(self):
        recognizers = {}
        for lang, path in self.vosk_models.items():
            if path.exists():
                try:
                    model = Model(str(path))
                    recognizers[lang] = KaldiRecognizer(model, 16000)
                    print(f"✅ Загрузка офлайн-модели VOSK: {lang.upper()}")
                except Exception as e:
                    print(f"⚠️ Ошибка загрузки модели VOSK ({lang}): {e}")
        return recognizers

    def listen_text(self, multilang=True):
        if self.mode == "online":
            return self._listen_online(multilang)
        else:
            return self._listen_offline(multilang)

    def _listen_online(self, multilang=True):
        with self.microphone as source:
            print("🎙️ (Online) Слушаю...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=6)
            except sr.WaitTimeoutError:
                return "", self.default_lang

        try:
            lang_code = self.default_lang
            text = self.recognizer.recognize_google(
                audio, language=f"{lang_code}-{lang_code.upper()}"
            )
            detected_lang = self.detect_language(text) if multilang else lang_code
            return text.strip(), detected_lang

        except sr.UnknownValueError:
            print("🤔 Не удалось распознать речь.")
            return "", self.default_lang
        except sr.RequestError:
            print("⚠️ Потеря соединения, переключаюсь в офлайн...")
            if self.config.get("auto_switch_mode", False):
                self._init_offline_recognition()
                return self._listen_offline(multilang)
            else:
                return "", self.default_lang

    def _listen_offline(self, multilang=True):
        lang = self.default_lang
        recognizer = self.vosk_recognizers.get(lang)
        if not recognizer:
            print(f"⚠️ Модель VOSK для {lang.upper()} не найдена.")
            return "", lang

        print(f"🎙️ (Offline {lang.upper()}) Говорите...")
        q = queue.Queue()

        def callback(indata, frames, time_, status):
            if status:
                print("⚠️", status)
            q.put(bytes(indata))

        with sr.Microphone(sample_rate=16000) as source, sd.RawInputStream(
            samplerate=16000,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=callback
        ):
            while True:
                data = q.get()
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "").strip()
                    if text:
                        detected_lang = self.detect_language(text)
                        return text, detected_lang

    def detect_language(self, text: str):
        text = text.strip().lower()
        if not text:
            return self.default_lang
        try:
            lang = detect(text)
            if lang in ["ru", "en", "uz"]:
                return lang
        except Exception:
            pass
        # Резервный способ по ключевым словам
        for code, words in DETECT_LANGUAGE_WORDS.items():
            if any(w in text for w in words):
                return code
        return self.default_lang
