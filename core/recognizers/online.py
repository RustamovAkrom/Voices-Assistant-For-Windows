from speech_recognition import (
    Recognizer,
    Microphone,
    WaitTimeoutError,
    UnknownValueError,
    RequestError,
)
from utils.logger import logger


class OnlineRecognizer:
    def __init__(self):
        self.recognizer = Recognizer()
        self.microphone = Microphone()

    def listen(self) -> str:
        """
        Function to listen for audio input and recognize speech using Google Speech Recognition.
        :return: Recognized text.
        """

        with self.microphone as source:
            logger.debug("Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            logger.debug("Listening for speach...")

            try:
                audio = self.recognizer.listen(source)

            except WaitTimeoutError:
                logger.warning("Timeout while waiting for audio input")
                return ""

            try:
                text = self.recognizer.recognize_google(audio, language="ru-RU").lower()
                logger.info(f"Recognized text: {text}")
                return text

            except UnknownValueError:
                logger.warning(
                    "Google Speech Recognition could not understand the audio"
                )
                return ""

            except RequestError:
                logger.error(
                    "Could not request results from Google Speech Recognition service"
                )
                return ""


__all__ = ("OnlineRecognizer",)
