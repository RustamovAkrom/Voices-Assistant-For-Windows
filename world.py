# from speaker.silero_tts import Speaker

# speaker = Speaker(device='cpu', language='ru', speaker='aidar_v2')

# speaker.say("Привет, как дела?")
# speaker.say("Это тестовое сообщение для проверки работы синтезатора речи.")
from speaker.voice_player import PlayAudio
import os

audio_file_path = r"media\audios\jarvis-og_greet1.wav"

print(os.path.exists(audio_file_path))

play_audio = PlayAudio()


# play_audio.play_audio(audio_file_path)
play_audio.play("off")
play_audio.play("not_found")
play_audio.play("stupid")
play_audio.play("ok")
play_audio.play("thanks")
