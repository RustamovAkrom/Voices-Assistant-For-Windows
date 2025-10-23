import json
import queue
from vosk import Model, KaldiRecognizer, SetLogLevel
import sounddevice as sd
from pathlib import Path


class OfflineRecognizer:
    def __init__(self, config, audio_queue):
        self.config = config
        self.audio_queue = audio_queue
        self.default_lang = config.get("assistant", {}).get("default_language", "ru")
        self.models_dir = Path("data/models")

        SetLogLevel(-1)
        model_path = self.models_dir / f"vosk-model-small-{self.default_lang}-0.22"
        if not model_path.exists():
            raise FileNotFoundError(f"⚠️ Нет модели для {self.default_lang}")

        self.model = Model(str(model_path))
        self.recognizer = KaldiRecognizer(self.model, 16000)

        # запускаем постоянный поток микрофона
        self.stream = sd.RawInputStream(
            samplerate=16000,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=self._callback
        )
        self.stream.start()
        print("🎤 (OFFLINE) Микрофон активен")

    def _callback(self, indata, frames, time_, status):
        if status:
            print(f"[Audio Warning] {status}")
        self.audio_queue.put(bytes(indata))

    def listen_text(self):
        try:
            data = self.audio_queue.get(timeout=5)
        except queue.Empty:
            return

        if self.recognizer.AcceptWaveform(data):
            result = json.loads(self.recognizer.Result())
            text = result.get("text", "").strip()
            if text:
                print(f"🗣️ {text}")
                return text, self.default_lang
