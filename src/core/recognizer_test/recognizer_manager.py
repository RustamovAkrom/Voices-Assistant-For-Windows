import threading
import queue
import time
from src.core.recognizer_test.online_recognizer import OnlineRecognizer
from src.core.recognizer_test.offline_recognizer import OfflineRecognizer


class RecognizerManager:
    def __init__(self, config):
        self.config = config
        self.default_lang = config.get("assistant", {}).get("default_language", "ru")

        self.audio_queue = queue.Queue()
        self.text_queue = queue.Queue()
        self.mode = "online"
        self.recognizers = {
            "online": OnlineRecognizer(config, self.audio_queue),
            "offline": OfflineRecognizer(config, self.audio_queue),
        }

        self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listener_thread.start()

    def _listen_loop(self):
        """Фоновое прослушивание микрофона и автоматическое переключение."""
        while True:
            recognizer = self.recognizers[self.mode]
            try:
                text, lang = recognizer.listen_text()
                if text:
                    self.text_queue.put((text, lang))
            except ConnectionError:
                print("⚠️ Интернет пропал — переключаюсь в OFFLINE.")
                self.mode = "offline"
            except Exception as e:
                print(f"[Recognizer Error] {e}")
                time.sleep(0.5)

    def get_text(self):
        """Забирает текст из очереди, если есть."""
        try:
            return self.text_queue.get_nowait()
        except queue.Empty:
            return None
