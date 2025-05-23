import pyaudio
import json
from vosk import Model, KaldiRecognizer


class OfflineRecognizer:
    model_path = "models/vosk"
    rate = 16000

    def __init__(self):
        self.model = Model(self.model_path)
        self.recognizer = KaldiRecognizer(self.model, self.rate)
        self.micraphone = pyaudio.PyAudio()
        self.format = pyaudio.paInt16

    def initializing_micraphone(self):
        self.stream = self.micraphone.open(
            format=self.format, 
            channels=1,
            rate=self.rate, 
            input=True, 
            frames_per_buffer=8000
        )

        self.stream.start_stream()

    def listen(self) -> str:
        data = self.stream.read(4000, exception_on_overflow=False)

        if self.recognizer.AcceptWaveform(data):
            result = json.loads(self.recognizer.Result()).get("text")
            return result
    
    def close_micraphone(self):
        self.micraphone.close(self.stream)


__all__ = ("OfflineRecognizer",)
