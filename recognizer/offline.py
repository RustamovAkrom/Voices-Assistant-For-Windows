import queue
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import numpy as np
from core.logger import logger


class OfflineRecognizer:
    def __init__(self, model_path: str, samplerate=16000):
        """
        Initialize the OfflineRecognizer with the given model path.
        :param model_path: Path to the Vosk model directory.
        """

        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, samplerate)
        self.q = queue.Queue()
        self.samplerate = samplerate

    def _callback(self, indata, frames, time, status):
        """
        Callback function to handle audio input.
        :param indata: Audio data.
        :param frames: Number of frames.
        :param time: Time information.
        :param status: Status information.
        """

        self.q.put(bytes(indata))

    def listen(self) -> str:
        """
        Function to listen for audio input and recognize speech using Vosk.
        :param timeout: Timeout for listening in seconds.
        :return: Recognized text.
        """
        with sd.RawInputStream(
            samplerate=16000, blocksize=8000,
            dtype='int16', channels=1,
            callback=self._callback
        ):
            logger.debug("Offline listening started...")
            while True:
                data = self.q.get()
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    return result.get("text", "")
            return ""

__all__ = ("OfflineRecognizer",)
