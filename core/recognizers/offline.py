import queue
import sounddevice as sd
import vosk
import json


class OfflineRecognizer:
    def __init__(self, model_path="data/models/vosk"):
        self.q = queue.Queue()
        self.model = vosk.Model(model_path)
        self.device = sd.default.device
        self.samplerate = int(
            sd.query_devices(self.device[0], "input")["default_samplerate"]
        )

    def callback(self, indata, frames, time, status):
        self.q.put(bytes(indata))

    def listen(self):
        with sd.RawInputStream(
            samplerate=self.samplerate,
            blocksize=8000,
            device=self.device[0],
            dtype="int16",
            channels=1,
            callback=self.callback,
        ):
            rec = vosk.KaldiRecognizer(self.model, self.samplerate)
            while True:
                data = self.q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result["text"]
                    return text


__all__ = ("OfflineRecognizer",)
