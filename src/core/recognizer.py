import os
import sys
import json
import queue
import requests
import zipfile
import sounddevice as sd
import numpy as np
import io
import tempfile
from pathlib import Path
from tqdm import tqdm
from vosk import Model, KaldiRecognizer, SetLogLevel
import speech_recognition as sr
from scipy.io.wavfile import write as wav_write


class Recognizer:
    """
    Голосовой Recognizer без PyAudio:
    - Онлайн через Google Speech
    - Оффлайн через Vosk
    - Работает с sounddevice
    """

    def __init__(self, config):
        self.config = config
        self.default_lang = config.get("assistant", {}).get("default_language", "ru")
        self.models_dir = Path("data/models")
        self.models_dir.mkdir(parents=True, exist_ok=True)

        # Пути к моделям
        self.vosk_models = {
            "ru": self.models_dir / "vosk-model-small-ru-0.22",
            "en": self.models_dir / "vosk-model-small-en-us-0.15",
            "uz": self.models_dir / "vosk-model-small-uz-0.22",
        }

        # Ссылки на скачивание
        self.vosk_urls = {
            "ru": "https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip",
            "en": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
            "uz": "https://alphacephei.com/vosk/models/vosk-model-small-uz-0.22.zip",
        }

        SetLogLevel(-1)
        self.online_available = self._check_internet()
        self._ensure_vosk_models()
        self.vosk_recognizers = self._load_vosk_recognizers()

        if self.online_available:
            self.mode = "online"
            print("🌐 Режим: ONLINE (Google Speech Recognition)")
        else:
            self.mode = "offline"
            print("⚙️ Режим: OFFLINE (Vosk Speech Recognition)")

    # === Проверка интернета ===
    def _check_internet(self):
        try:
            requests.get("https://www.google.com", timeout=3)
            return True
        except requests.RequestException:
            return False

    # === Скачать модели Vosk ===
    def _ensure_vosk_models(self):
        for lang, path in self.vosk_models.items():
            if not path.exists():
                if self.online_available:
                    print(f"📦 Скачиваю модель для {lang.upper()}...")
                    self._download_model(self.vosk_urls[lang])
                else:
                    print(f"❌ Нет модели для {lang.upper()} и нет интернета для загрузки.")
                    sys.exit(1)

    def _download_model(self, url):
        tmp_dir = tempfile.gettempdir()
        tmp_file = os.path.join(tmp_dir, "vosk_model.zip")
        print(f"⬇️ Загружаю модель из {url}")

        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            total = int(r.headers.get("Content-Length", 0))
            with open(tmp_file, "wb") as f, tqdm(
                total=total, unit="B", unit_scale=True, desc="📦 Загрузка"
            ) as bar:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        bar.update(len(chunk))

        if not zipfile.is_zipfile(tmp_file):
            print("❌ Ошибка: загруженный файл не ZIP.")
            sys.exit(1)

        with zipfile.ZipFile(tmp_file, "r") as zf:
            zf.extractall(self.models_dir)

        os.remove(tmp_file)
        print("✅ Модель успешно установлена!")

    # === Загрузка моделей ===
    def _load_vosk_recognizers(self):
        recs = {}
        for lang, path in self.vosk_models.items():
            if path.exists():
                try:
                    model = Model(str(path))
                    recs[lang] = KaldiRecognizer(model, 16000)
                    print(f"✅ Загрузил офлайн модель: {lang.upper()}")
                except Exception as e:
                    print(f"⚠️ Ошибка при загрузке {lang}: {e}")
        return recs

    # === Основное прослушивание ===
    def listen_text(self, multilang=True):
        if self.mode == "online":
            return self._listen_online(multilang)
        else:
            return self._listen_offline()

    # === Онлайн через sounddevice + Google Speech ===
    def _listen_online(self, multilang=True):
        print("🎙️ (Online) Говорите...")

        samplerate = 16000
        duration = 5  # секунд записи

        audio_data = sd.rec(
            int(samplerate * duration),
            samplerate=samplerate,
            channels=1,
            dtype="int16"
        )
        sd.wait()

        # Конвертируем в AudioData (для speech_recognition)
        wav_bytes = io.BytesIO()
        wav_write(wav_bytes, samplerate, audio_data)
        wav_bytes.seek(0)

        r = sr.Recognizer()
        with sr.AudioFile(wav_bytes) as source:
            audio = r.record(source)

        try:
            lang_code = self.default_lang
            text = r.recognize_google(audio, language=f"{lang_code}-{lang_code.upper()}")
            detected_lang = self.detect_language(text) if multilang else lang_code
            print(f"🗣️ {text}")
            return text, detected_lang
        except sr.UnknownValueError:
            print("🤔 Не понял, повторите...")
            return "", self.default_lang
        except sr.RequestError:
            print("⚠️ Интернет пропал — офлайн режим.")
            self.mode = "offline"
            return self._listen_offline()

    # === Офлайн через Vosk ===
    def _listen_offline(self):
        lang = self.default_lang
        recognizer = self.vosk_recognizers.get(lang)
        if not recognizer:
            print(f"⚠️ Модель для {lang.upper()} не найдена.")
            return "", lang

        print(f"🎙️ (Offline {lang.upper()}) Говорите...")

        q = queue.Queue()

        def callback(indata, frames, time_, status):
            q.put(bytes(indata))

        with sd.RawInputStream(samplerate=16000, blocksize=8000,
                               dtype="int16", channels=1, callback=callback):
            while True:
                data = q.get()
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "").strip()
                    if text:
                        detected_lang = self.detect_language(text)
                        print(f"🗣️ {text}")
                        return text, detected_lang

    # === Простое определение языка ===
    def detect_language(self, text):
        text = text.lower()
        en_words = {"hello", "thanks", "how", "you", "open", "music"}
        uz_words = {"salom", "rahmat", "qandaysiz", "yaxshi"}
        ru_words = {"привет", "спасибо", "открой", "включи", "поставь"}

        if any(w in text for w in en_words):
            return "en"
        elif any(w in text for w in uz_words):
            return "uz"
        elif any(w in text for w in ru_words):
            return "ru"
        return self.default_lang

# import os
# import sys
# import json
# import queue
# import zipfile
# import urllib.request
# from io import BytesIO
# from pathlib import Path
# import sounddevice as sd
# import speech_recognition as sr
# from vosk import Model, KaldiRecognizer, SetLogLevel
# from langdetect import detect, DetectorFactory

# from src.core.config import MODELS_DIR, VOSK_MODEL_URLS, DETECT_LANGUAGE_WORDS, get_settings
# from src.utils.base import check_internet

# # Фиксируем seed для детерминированности langdetect:contentReference[oaicite:3]{index=3}
# DetectorFactory.seed = 0

# class Recognizer:
#     def __init__(self, config):
#         self.config = config
#         self.default_lang = config.get("assistant", {}).get("default_language", "ru")
#         self.models_dir = MODELS_DIR
#         self.models_dir.mkdir(parents=True, exist_ok=True)

#         self.vosk_models = {
#             "ru": self.models_dir / "vosk-model-small-ru-0.22",
#             "en": self.models_dir / "vosk-model-small-en-us-0.15",
#             "uz": self.models_dir / "vosk-model-small-uz-0.22",
#         }

#         SetLogLevel(-1)
#         self.online_available = check_internet()

#         # Если режим офлайн по настройке, сразу переходим в офлайн
#         if self.config.get("offline_mode", False):
#             self.online_available = False
#         # Обеспечение наличия моделей VOSK
#         self._ensure_vosk_models()
#         self.vosk_recognizers = self._load_vosk_recognizers()

#         if self.online_available:
#             self._init_online_recognition()
#         else:
#             self._init_offline_recognition()

#     def _init_online_recognition(self):
#         self.mode = "online"
#         self.recognizer = sr.Recognizer()
#         self.microphone = sr.Microphone()
#         print("🌐 Режим распознавания: ONLINE")

#     def _init_offline_recognition(self):
#         self.mode = "offline"
#         print("⚙️ Режим распознавания: OFFLINE")

#     def _ensure_vosk_models(self):
#         for lang, path in self.vosk_models.items():
#             if not path.exists():
#                 if self.online_available:
#                     print(f"📦 Скачиваю модель VOSK для {lang.upper()}...")
#                     try:
#                         self._download_and_extract(VOSK_MODEL_URLS[lang], self.models_dir)
#                         print(f"✅ Модель установлена: {path.name}")
#                     except Exception as e:
#                         print(f"❌ Ошибка при скачивании модели {lang}: {e}")
#                         # не выходим из программы, просто предупреждаем
#                 else:
#                     print(f"⚠️ Модель для {lang.upper()} не найдена (офлайн режим недоступен для этого языка).")
#                     # не выходим, просто пропускаем

#     def _download_and_extract(self, url, target_dir):
#         with urllib.request.urlopen(url) as resp:
#             with zipfile.ZipFile(BytesIO(resp.read())) as zf:
#                 zf.extractall(self.models_dir)

#     def _load_vosk_recognizers(self):
#         recognizers = {}
#         for lang, path in self.vosk_models.items():
#             if path.exists():
#                 try:
#                     model = Model(str(path))
#                     recognizers[lang] = KaldiRecognizer(model, 16000)
#                     print(f"✅ Загрузка офлайн-модели VOSK: {lang.upper()}")
#                 except Exception as e:
#                     print(f"⚠️ Ошибка загрузки модели VOSK ({lang}): {e}")
#         return recognizers

#     def listen_text(self, multilang=True):
#         if self.mode == "online":
#             return self._listen_online(multilang)
#         else:
#             return self._listen_offline(multilang)

#     def _listen_online(self, multilang=True):
#         with self.microphone as source:
#             print("🎙️ (Online) Слушаю...")
#             self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
#             try:
#                 audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=6)
#             except sr.WaitTimeoutError:
#                 return "", self.default_lang

#         try:
#             lang_code = self.default_lang
#             text = self.recognizer.recognize_google(
#                 audio, language=f"{lang_code}-{lang_code.upper()}"
#             )
#             detected_lang = self.detect_language(text) if multilang else lang_code
#             return text.strip(), detected_lang

#         except sr.UnknownValueError:
#             print("🤔 Не удалось распознать речь.")
#             return "", self.default_lang
#         except sr.RequestError:
#             print("⚠️ Потеря соединения, переключаюсь в офлайн...")
#             if self.config.get("auto_switch_mode", False):
#                 self._init_offline_recognition()
#                 return self._listen_offline(multilang)
#             else:
#                 return "", self.default_lang

#     def _listen_offline(self, multilang=True):
#         lang = self.default_lang
#         recognizer = self.vosk_recognizers.get(lang)
#         if not recognizer:
#             print(f"⚠️ Модель VOSK для {lang.upper()} не найдена.")
#             return "", lang

#         print(f"🎙️ (Offline {lang.upper()}) Говорите...")
#         q = queue.Queue()

#         def callback(indata, frames, time_, status):
#             if status:
#                 print("⚠️", status)
#             q.put(bytes(indata))

#         with sr.Microphone(sample_rate=16000) as source, sd.RawInputStream(
#             samplerate=16000,
#             blocksize=8000,
#             dtype="int16",
#             channels=1,
#             callback=callback
#         ):
#             while True:
#                 data = q.get()
#                 if recognizer.AcceptWaveform(data):
#                     result = json.loads(recognizer.Result())
#                     text = result.get("text", "").strip()
#                     if text:
#                         detected_lang = self.detect_language(text)
#                         return text, detected_lang

#     def detect_language(self, text: str):
#         text = text.strip().lower()
#         if not text:
#             return self.default_lang
#         try:
#             lang = detect(text)
#             if lang in ["ru", "en", "uz"]:
#                 return lang
#         except Exception:
#             pass
#         # Резервный способ по ключевым словам
#         for code, words in DETECT_LANGUAGE_WORDS.items():
#             if any(w in text for w in words):
#                 return code
#         return self.default_lang
