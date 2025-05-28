import sounddevice as sd
import soundfile as sf
import random


AUDIO_FILES = {
    "great": r"data\media\audios\jarvis-og_greet1.wav",
    "not_found": r"data\media\audios\jarvis-og_not_found.wav",
    "off": r"data\media\audios\jarvis-og_off.wav",
    "run": r"data\media\audios\jarvis-og_run.wav",
    "stupid": r"data\media\audios\jarvis-og_stupid.wav",
    "ok": r"data\media\audios\jarvis-og_ok1.wav",
    "thanks": r"data\media\audios\jarvis-og_thanks.wav",
}


class PlayAudio:
    def __init__(self):
        self.base_path = r"data\media\audios"
        self.audio_files = AUDIO_FILES
    
    def play(self, name: str):
        if name not in self.audio_files:
            print(f"Audio file '{name}' not found in the audio files dictionary.")
            return
        
        file_path = self.audio_files.get(name, None)

        self.play_audio(file_path)

    def play_audio(self, file_path: str):
        data, samplerate = sf.read(file_path)
        sd.play(data, samplerate)
        sd.wait()