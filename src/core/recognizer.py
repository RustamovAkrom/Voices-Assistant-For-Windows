import os
import sys
import json
import queue
import requests
import zipfile
import sounddevice as sd
import io
import tempfile
from pathlib import Path
from tqdm import tqdm
from vosk import Model, KaldiRecognizer, SetLogLevel
import speech_recognition as sr
from scipy.io.wavfile import write as wav_write


class Recognizer:
    """
    Постоянно активный Recognizer:
    - Онлайн (Google Speech)
    - Оффлайн (Vosk)
    - Микрофон не выключается между фразами
    """

    def __init__(self, config):
        self.config = config
        self.default_lang = config.get("assistant", {}).get("default_language", "ru")
        self.language_map = {"ru": "ru-RU", "en": "en-US", "uz": "uz-UZ"}

        self.models_dir = Path("data/models")
        self.models_dir.mkdir(parents=True, exist_ok=True)

        self.vosk_models = {
            "ru": self.models_dir / "vosk-model-small-ru-0.22",
            "en": self.models_dir / "vosk-model-small-en-us-0.15",
            "uz": self.models_dir / "vosk-model-small-uz-0.22",
        }

        self.vosk_urls = {
            "ru": "https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip",
            "en": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
            "uz": "https://alphacephei.com/vosk/models/vosk-model-small-uz-0.22.zip",
        }

        SetLogLevel(-1)
        self.online_available = self._check_internet()
        self._ensure_vosk_models()
        self.vosk_recognizers = self._load_vosk_recognizers()

        self.mode = "online" if self.online_available else "offline"
        print(f"🌐 Режим: {self.mode.upper()}")
        print(f"🗣️ Текущий язык: {self.default_lang.upper()}")

        # Очередь аудио и постоянный поток
        self.audio_queue = queue.Queue()
        self.stream = None
        self._start_microphone_stream()

    # === Интернет ===
    def _check_internet(self):
        try:
            requests.get("https://www.google.com", timeout=3)
            return True
        except requests.RequestException:
            return False

    # === Проверяем модели ===
    def _ensure_vosk_models(self):
        for lang, path in self.vosk_models.items():
            if not path.exists() and self.online_available:
                print(f"📦 Скачиваю модель для {lang.upper()}...")
                self._download_model(self.vosk_urls[lang])

    def _download_model(self, url):
        tmp_file = Path(tempfile.gettempdir()) / "vosk_model.zip"
        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            total = int(r.headers.get("Content-Length", 0))
            with open(tmp_file, "wb") as f, tqdm(total=total, unit="B", unit_scale=True) as bar:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        bar.update(len(chunk))

        with zipfile.ZipFile(tmp_file, "r") as zf:
            zf.extractall(self.models_dir)
        os.remove(tmp_file)
        print("✅ Модель установлена!")

    # === Загружаем модели Vosk ===
    def _load_vosk_recognizers(self):
        recs = {}
        for lang, path in self.vosk_models.items():
            if path.exists():
                model = Model(str(path))
                recs[lang] = KaldiRecognizer(model, 16000)
        return recs

    # === Постоянный аудиопоток ===
    def _start_microphone_stream(self):
        def callback(indata, frames, time_, status):
            if status:
                print(f"[AUDIO WARNING] {status}")
            self.audio_queue.put(bytes(indata))

        print("🎤 Микрофон активен (постоянный режим)")
        self.stream = sd.RawInputStream(
            samplerate=16000,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=callback
        )
        self.stream.start()

    # === Главный метод ===
    def listen_text(self):
        """
        Слушает микрофон постоянно и возвращает текст, когда распознана фраза.
        """
        if self.mode == "online":
            return self._listen_online()
        else:
            return self._listen_offline()

    # === Онлайн (Google) ===
    def _listen_online(self):
        print("🎙️ (Online) Говорите...")

        samplerate = 16000
        duration = 5

        try:
            with sd.InputStream(samplerate=samplerate, channels=1, dtype="int16") as stream:
                audio_data = stream.read(int(samplerate * duration))[0]
        except Exception as e:
            print(f"⚠️ Ошибка аудио-потока: {e}")
            return "", self.default_lang

        # Конвертация в wav и Google Speech
        wav_bytes = io.BytesIO()
        wav_write(wav_bytes, samplerate, audio_data)
        wav_bytes.seek(0)

        r = sr.Recognizer()
        with sr.AudioFile(wav_bytes) as source:
            audio = r.record(source)

        lang_code = self.language_map.get(self.default_lang, "ru-RU")
        try:
            text = r.recognize_google(audio, language=lang_code)
            print(f"🧠 Распознано ({self.default_lang.upper()}): {text}")
            return text, self.default_lang
        except sr.UnknownValueError:
            print("🤔 Не понял, повторите...")
            return "", self.default_lang
        except sr.RequestError:
            print("⚠️ Интернет пропал — офлайн режим.")
            self.mode = "offline"
            return self._listen_offline()

    # === Офлайн (Vosk) ===
    def _listen_offline(self):
        lang = self.default_lang
        recognizer = self.vosk_recognizers.get(lang)
        if not recognizer:
            print(f"⚠️ Нет модели для {lang.upper()}")
            return "", lang

        while True:
            data = self.audio_queue.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").strip()
                if text:
                    print(f"🗣️ {text}")
                    return text, lang

    # === Сбор данных ===
    def _collect_audio(self, seconds=5):
        """Собирает аудио блоки за указанное время."""
        frames = []
        start = sd.get_stream().time if self.stream else 0
        duration = seconds
        while True:
            try:
                frames.append(self.audio_queue.get(timeout=seconds))
                if len(frames) * 0.5 > duration:  # приблизительно seconds
                    break
            except queue.Empty:
                break
        if not frames:
            return None
        import numpy as np
        return np.frombuffer(b"".join(frames), dtype="int16")
