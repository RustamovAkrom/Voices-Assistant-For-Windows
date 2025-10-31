import pvporcupine
import sounddevice as sd
import numpy as np
import logging
import time
import sys

logger = logging.getLogger("Porcupine")

class PorcupineListener:
    def __init__(self, keyword="jarvis", sensitivity=0.6):
        self.keyword = keyword.lower()
        self.sensitivity = sensitivity
        self.active = False
        self.handle = None
        self.stream = None

        try:
            # Проверяем доступные ключевые слова
            available = pvporcupine.KEYWORDS
            if self.keyword not in available:
                logger.warning(f"⚠️ Ключевое слово '{self.keyword}' не найдено. "
                               f"Доступные: {', '.join(available)}. "
                               f"Используется 'jarvis'.")
                self.keyword = "jarvis"

            # Инициализация Porcupine
            self.handle = pvporcupine.create(
                access_key="hJ3LqXL7Ef37ovssvvLNsC2EFDWOtIMaaPxKso6xzTtaySdopJTIFQ==",
                keywords=[self.keyword],
                sensitivities=[self.sensitivity]
            )

            logger.info(f"🎙️ Porcupine активирован с wake word: '{self.keyword}'")

        except Exception as e:
            logger.error(f"❌ Ошибка инициализации Porcupine: {e}")
            sys.exit(1)

    def listen(self):
        """Слушает wake word, возвращает True, если активировано"""
        self.active = True
        logger.info("👂 Ожидание активационного слова...")

        try:
            def audio_callback(indata, frames, time_info, status):
                if status:
                    logger.warning(f"[AUDIO] {status}")
                pcm = (indata[:, 0] * 32768).astype(np.int16)
                result = self.handle.process(pcm)
                if result >= 0:
                    self.active = False
                    raise StopIteration  # завершить stream safely

            with sd.InputStream(
                samplerate=self.handle.sample_rate,
                channels=1,
                dtype="float32",
                callback=audio_callback
            ):
                while self.active:
                    time.sleep(0.01)

        except StopIteration:
            logger.info(f"✅ Wake word '{self.keyword}' обнаружено!")
            return True

        except Exception as e:
            logger.error(f"Ошибка прослушивания: {e}")
            return False

    def stop(self):
        """Останавливает Porcupine и освобождает ресурсы"""
        self.active = False
        if self.handle:
            self.handle.delete()
        logger.info("🛑 Porcupine остановлен.")
