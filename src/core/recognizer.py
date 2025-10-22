import os
import sys
import json
import queue
import requests
import zipfile
import urllib.request
from io import BytesIO
from pathlib import Path
import speech_recognition as sr
from vosk import Model, KaldiRecognizer, SetLogLevel
import sounddevice as sd
from tqdm import tqdm
import tempfile
import shutil

class Recognizer:
    """
    Voice Recognizer for Voices Assistant
    - Автоматически использует Google Speech (онлайн) или Vosk (офлайн)
    - Поддерживает русский, английский, узбекский языки
    - Сам скачивает и кэширует модели
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

        SetLogLevel(-1)  # Отключаем логи Vosk

        self.online_available = self._check_internet()
        self._ensure_vosk_models()
        self.vosk_recognizers = self._load_vosk_recognizers()

        if self.online_available:
            self._init_online_recognition()
        else:
            self._init_offline_recognition()

    # === Проверка интернет-соединения ===
    def _check_internet(self) -> bool:
        try:
            requests.get("https://www.google.com", timeout=3)
            return True
        except requests.RequestException:
            return False

    # === Инициализация Google Speech ===
    def _init_online_recognition(self):
        self.mode = "online"
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        print("🌐 Режим: ONLINE (Google Speech Recognition)")

    # === Инициализация Vosk ===
    def _init_offline_recognition(self):
        self.mode = "offline"
        print("⚙️ Режим: OFFLINE (Vosk Speech Recognition)")

    # === Скачивание офлайн моделей ===
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
        """Скачивает и распаковывает модель с прогрессом и защитой"""

        try:
            # Создаём временный файл для загрузки
            tmp_dir = tempfile.gettempdir()
            tmp_file = os.path.join(tmp_dir, "vosk_model.zip")

            print(f"⬇️ Загружаю модель из {url}")

            # Загружаем с отображением прогресса
            with requests.get(url, stream=True, timeout=30) as r:
                r.raise_for_status()
                total = int(r.headers.get("Content-Length", 0))

                if "text/html" in r.headers.get("Content-Type", ""):
                    print("❌ Ошибка: вместо архива получен HTML (скорее всего, ссылка устарела).")
                    print("   Попробуйте вручную скачать модель с https://alphacephei.com/vosk/models")
                    sys.exit(1)

                with open(tmp_file, "wb") as f, tqdm(
                    total=total, unit="B", unit_scale=True, desc="📦 Загрузка"
                ) as bar:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            bar.update(len(chunk))

            # Проверяем, что файл — это zip
            if not zipfile.is_zipfile(tmp_file):
                print("❌ Ошибка: загруженный файл не является ZIP-архивом.")
                print("   Возможно, Vosk изменил ссылку или сервер временно недоступен.")
                print("   Скачайте вручную модель и распакуйте в data/models.")
                sys.exit(1)

            # Распаковка
            with zipfile.ZipFile(tmp_file, "r") as zf:
                zf.extractall(self.models_dir)

            print("✅ Модель успешно установлена!")

        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка сети: {e}")
            print("   Проверьте интернет и попробуйте снова.")
            sys.exit(1)
        except zipfile.BadZipFile:
            print("❌ Повреждённый ZIP-файл. Удалите его и повторите загрузку.")
            sys.exit(1)
        except Exception as e:
            print(f"⚠️ Непредвиденная ошибка: {e}")
            sys.exit(1)
        finally:
            # Очищаем временный файл
            if os.path.exists(tmp_file):
                os.remove(tmp_file)

    # === Загрузка моделей в память ===
    def _load_vosk_recognizers(self):
        recognizers = {}
        for lang, path in self.vosk_models.items():
            if path.exists():
                try:
                    model = Model(str(path))
                    recognizers[lang] = KaldiRecognizer(model, 16000)
                    print(f"✅ Загрузил офлайн модель: {lang.upper()}")
                except Exception as e:
                    print(f"⚠️ Ошибка при загрузке {lang}: {e}")
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

    # === Главная функция прослушивания ===
    def listen_text(self, multilang=True):
        if self.mode == "online":
            return self._listen_online(multilang)
        else:
            return self._listen_offline()

    # === Онлайн режим ===
    def _listen_online(self, multilang=True):
        try:
            with self.microphone as source:
                print("🎙️ Говорите (онлайн)...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=7)

            lang_code = self.default_lang
            text = self.recognizer.recognize_google(audio, language=f"{lang_code}-{lang_code.upper()}")
            detected_lang = self.detect_language(text) if multilang else lang_code
            return text, detected_lang

        except sr.UnknownValueError:
            print("🤔 Не понял, повторите...")
            return "", self.default_lang
        except sr.RequestError:
            print("⚠️ Интернет пропал — переключаюсь в офлайн режим.")
            self._init_offline_recognition()
            return self._listen_offline()
        except Exception as e:
            print(f"⚠️ Ошибка распознавания: {e}")
            return "", self.default_lang

    # === Офлайн режим ===
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
