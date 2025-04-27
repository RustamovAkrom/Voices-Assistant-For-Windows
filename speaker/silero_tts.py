import torch
import sounddevice as sd

class Speaker:
    def __init__(self, device='cpu', language='ru', speaker='aidar_v2'):
        self.device = device
        self.language = language
        # Загрузка модели TTS
        self.model = torch.hub.load(
            repo_or_dir='snakers4/silero-models',
            model='silero_tts',
            language=language,
            trust_repo=True
        ).to(self.device)
        
        self.sample_rate = 48000  # Устанавливаем частоту дискретизации

    def say(self, text: str):
        # Генерация аудио из текста
        audio = self.model.apply_tts(
            texts=[text],  # Передаем текст в виде списка
            sample_rate=self.sample_rate,
            device=self.device
        )

        # Проигрывание с использованием sounddevice
        sd.play(audio, samplerate=self.sample_rate)
        sd.wait()  # Ожидаем окончания воспроизведения аудио
