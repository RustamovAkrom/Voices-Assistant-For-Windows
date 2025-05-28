import queue
import sounddevice as sd
import vosk
import json

 
class OfflineRecognizer:
    def __init__(self):
        self.q = queue.Queue()
        self.model = vosk.Model("data/models/vosk")
        self.device = sd.default.device
        self.samplerate = int(sd.query_devices(self.device[0], 'input')['default_samplerate'])

    def callback(self, indata, frames, time, status):
        self.q.put(bytes(indata))

    def listen(self):
        with sd.RawInputStream(samplerate=self.samplerate, blocksize=8000, device=self.device[0], dtype='int16', channels=1, callback=self.callback):
            rec = vosk.KaldiRecognizer(self.model, self.samplerate)
            while True:
                data = self.q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result['text']
                    return text

# class OfflineRecognizer:
#     model_path = "models/vosk"
#     rate = 16000

#     def __init__(self):
#         self.model = Model(self.model_path)
#         self.recognizer = KaldiRecognizer(self.model, self.rate)
#         self.micraphone = pyaudio.PyAudio()
#         self.format = pyaudio.paInt16

#     def initializing_micraphone(self):
#         self.stream = self.micraphone.open(
#             format=self.format, 
#             channels=1,
#             rate=self.rate, 
#             input=True, 
#             frames_per_buffer=8000
#         )

#         self.stream.start_stream()

#     def listen(self) -> str:
#         data = self.stream.read(4000, exception_on_overflow=False)

#         if self.recognizer.AcceptWaveform(data):
#             result = json.loads(self.recognizer.Result()).get("text")
#             return result
    
#     def close_micraphone(self):
#         self.micraphone.close(self.stream)


__all__ = ("OfflineRecognizer",)
