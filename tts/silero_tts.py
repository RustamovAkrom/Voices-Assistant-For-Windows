import torch
import sounddevice as sd
import time


class Speaker:
    language: str = 'ru'  # Язык
    model_id: str = 'ru_v3'  # Идентификатор модели
    sample_rate: int = 48000  # Частота дискретизации
    speaker: str = 'aidar'  # Имя спикера
    put_accent: bool = True  # Учитывать ударение
    put_yo: bool = True  # Учитывать букву ё
    device: str = torch.device('cpu')  # Устройство для вычислений (CPU или GPU)

    def __init__(self):
        # Загрузка модели TTS
        self.model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                       model='silero_tts',
                                       language=self.get_arguments()['language'],
                                       speaker=self.get_arguments()['model_id'],
                                       )
        self.model.to(self.device)

    @classmethod
    def get_arguments(cls) -> dict:
        return {
            'language': cls.language,
            'model_id': cls.model_id,
            'sample_rate': cls.sample_rate,
            'speaker': cls.speaker,
            'put_accent': cls.put_accent,
            'put_yo': cls.put_yo,
            'device': cls.device
        }
    
    def say(self, text: str):
        audio = self.model.apply_tts(text=text + "..",
                                    speaker=self.get_arguments()['speaker'],
                                    sample_rate=self.get_arguments()['sample_rate'],
                                    put_accent=self.get_arguments()['put_accent'],
                                    put_yo=self.get_arguments()['put_yo'],
                                    )
        sd.play(audio, self.get_arguments()['sample_rate'] * 1.05)
        time.sleep((len(audio) / self.get_arguments()['sample_rate']) * 1.05)
        sd.stop()
