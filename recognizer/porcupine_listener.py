# activation/porcupine_listener.py
import struct
import pyaudio
from pvporcupine import create


class PorcupineListener:
    def __init__(self, keywords=("jarvis",), access_key=None):
        if access_key is None:
            raise ValueError("Porcupine access_key required!")
        self.porcupine = create(
            keywords=list(keywords),
            access_key=access_key,
            sensitivities=[0.5] * len(keywords),
        )
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=512,
        )

    def listen(self):
        """Блокирующе ждет активационное слово. Возвращает True при срабатывании."""
        while True:
            pcm = self.stream.read(512)
            pcm = struct.unpack_from("h" * 512, pcm)
            result = self.porcupine.process(pcm)
            if result >= 0:
                return True

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()
