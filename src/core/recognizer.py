import os
import sys
import json
import queue
import requests
import speech_recognition as sr
from pathlib import Path
from vosk import Model, KaldiRecognizer, SetLogLevel


class Recognizer:
    def __init__(self, config):
        self.config = config
        self.default_lang = config.get("assistant", {}).get("default_language", "ru")
        self.models_dir = Path("data/models")
        self.models_dir.mkdir(parents=True, exist_ok=True)

        # Пути к моделям
        self.vosk_models = {
            "ru": str(self.models_dir / "vosk-model-small-ru-0.22"),
            "en": str(self.models_dir / "vosk-model-small-en-us-0.15"),
            "uz": str(self.models_dir / "vosk-model-small-uz-0.22"),
        }

        SetLogLevel(-1)  # Отключаем логи Vosk

        # Проверяем интернет
        self.online_available = self.check_internet()

        # Всегда проверяем и устанавливаем офлайн модели (если не установлены)
        self._ensure_vosk_models()

        # Загружаем модели в память
        self.vosk_recognizers = self._load_vosk_recognizers()

        # После загрузки решаем — онлайн или офлайн
        if self.online_available:
            self._init_online_recognition()
        else:
            self._init_offline_recognition()

    # === Проверка подключения к интернету ===
    def check_internet(self) -> bool:
        try:
            requests.get("https://www.google.com", timeout=3)
            return True
        except requests.RequestException:
            return False

    # === Инициализация Google Speech Recognition ===
    def _init_online_recognition(self):
        self.mode = "online"
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        print("🌐 Режим: ONLINE (Google Speech Recognition)")

    # === Инициализация офлайн режима ===
    def _init_offline_recognition(self):
        self.mode = "offline"
        print("⚙️ Режим: OFFLINE (Vosk Speech Recognition)")

    # === Проверка и скачивание vosk моделей ===
    def _ensure_vosk_models(self):
        urls = {
            "ru": "https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip",
            "en": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
            "uz": "https://alphacephei.com/vosk/models/vosk-model-small-uz-0.22.zip",
        }

        for lang, path in self.vosk_models.items():
            if not os.path.exists(path):
                if self.online_available:
                    print(f"📦 Скачиваю офлайн модель для {lang.upper()}...")
                    self._download_and_extract(urls[lang], path)
                else:
                    print(f"❌ Нет модели для {lang.upper()} и нет интернета для загрузки.")
                    print("   Подключите интернет и перезапустите Jarvis для первой установки.")
                    sys.exit(1)

    # === Скачивание и распаковка модели ===
    def _download_and_extract(self, url, target_dir):
        import zipfile
        import urllib.request
        from io import BytesIO

        try:
            with urllib.request.urlopen(url) as resp:
                with zipfile.ZipFile(BytesIO(resp.read())) as zf:
                    zf.extractall(self.models_dir)
            print(f"✅ Модель успешно установлена: {target_dir}")
        except Exception as e:
            print(f"❌ Ошибка при установке модели {target_dir}: {e}")
            sys.exit(1)

    # === Загрузка моделей в память ===
    def _load_vosk_recognizers(self):
        recognizers = {}
        for lang, path in self.vosk_models.items():
            if os.path.exists(path):
                try:
                    model = Model(path)
                    recognizers[lang] = KaldiRecognizer(model, 16000)
                    print(f"✅ Загружена офлайн модель: {lang.upper()}")
                except Exception as e:
                    print(f"⚠️ Ошибка при загрузке модели {lang}: {e}")
        return recognizers

    # === Определение языка ===
    def detect_language(self, text: str):
        text = text.lower()
        en_words = {"hello", "thanks", "how", "you", "open", "music"}
        uz_words = {"salom", "rahmat", "qandaysiz", "yaxshi"}
        ru_words = {"привет", "спасибо", "открой", "включи", "поставь"}

        if any(word in text for word in en_words):
            return "en"
        elif any(word in text for word in uz_words):
            return "uz"
        elif any(word in text for word in ru_words):
            return "ru"
        return self.default_lang

    # === Основная функция для прослушивания ===
    def listen_text(self, multilang=True):
        if self.mode == "online":
            return self._listen_online(multilang)
        else:
            return self._listen_offline()

    # === Онлайн распознавание ===
    def _listen_online(self, multilang=True):
        with self.microphone as source:
            print("🎙️ Слушаю вас (онлайн)...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=7)

        try:
            lang_code = self.default_lang
            text = self.recognizer.recognize_google(audio, language=f"{lang_code}-{lang_code.upper()}")
            detected_lang = self.detect_language(text) if multilang else lang_code
            return text, detected_lang
        except sr.UnknownValueError:
            print("🤔 Не понял, повторите...")
            return "", self.default_lang
        except sr.RequestError:
            print("⚠️ Интернет пропал. Перехожу в офлайн режим.")
            self._init_offline_recognition()
            return self._listen_offline()

    # === Офлайн распознавание ===
    def _listen_offline(self):
        import sounddevice as sd

        lang = self.default_lang
        recognizer = self.vosk_recognizers.get(lang)
        if not recognizer:
            print(f"⚠️ Модель для {lang.upper()} не найдена.")
            return "", lang

        print(f"🎙️ (Offline {lang.upper()}) Говорите...")

        q = queue.Queue()

        def callback(indata, frames, time_, status):
            q.put(bytes(indata))

        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16",
                               channels=1, callback=callback):
            while True:
                data = q.get()
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "").strip()
                    if text:
                        detected_lang = self.detect_language(text)
                        return text, detected_lang

"""
| Функция                 | Что делает                                           |
| ----------------------- | ---------------------------------------------------- |
| `check_internet()`      | Проверяет подключение и решает, какой режим включить |
| `_ensure_vosk_models()` | Скачивает нужные модели автоматически                |
| `_listen_online()`      | Использует Google Speech Recognition                 |
| `_listen_offline()`     | Использует Vosk и `sounddevice`                      |
| `detect_language()`     | Простейшая логика для RU/EN/UZ                       |
| `default_language`      | Настраивается через `config.yaml`                    |

"""