import torch
import sounddevice as sd
import time


class Speaker:
    language: str = "ru"  # Язык
    model_id: str = "ru_v3"  # Идентификатор модели
    sample_rate: int = 48000  # Частота дискретизации
    speaker: str = "aidar"  # Имя спикера
    put_accent: bool = True  # Учитывать ударение
    put_yo: bool = True  # Учитывать букву ё
    device: str = torch.device("cpu")  # Устройство для вычислений (CPU или GPU)

    def __init__(self):
        # Загрузка модели TTS
        self.model, _ = torch.hub.load(
            repo_or_dir="snakers4/silero-models",
            model="silero_tts",
            language=self.language,
            speaker=self.model_id,
        )
        self.model.to(self.device)

    def say(self, text: str):
        audio = self.model.apply_tts(
            text=text + "..",
            speaker=self.speaker,
            sample_rate=self.sample_rate,
            put_accent=self.put_accent,
            put_yo=self.put_yo,
        )
        sd.play(audio, self.sample_rate * 1.05)
        time.sleep((len(audio) / self.sample_rate * 1.05))
        sd.stop()
