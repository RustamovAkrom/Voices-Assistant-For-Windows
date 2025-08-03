import sounddevice as sd
import soundfile as sf


AUDIO_FILES = {
    "great1": r"data\media\audios\jarvis-og_greet1.wav",
    "great2": r"data\media\audios\jarvis-og_greet2.wav",
    "great3": r"data\media\audios\jarvis-og_greet3.wav",
    "run1": r"data\media\audios\jarvis-og_run1.wav",
    "run2": r"data\media\audios\jarvis-og_run2.wav",
    "ok1": r"data\media\audios\jarvis-og_ok1.wav",
    "ok2": r"data\media\audios\jarvis-og_ok2.wav",
    "ok3": r"data\media\audios\jarvis-og_ok3.wav",
    "off": r"data\media\audios\jarvis-og_off.wav",
    "not_found": r"data\media\audios\jarvis-og_not_found.wav",
    "stupid": r"data\media\audios\jarvis-og_stupid.wav",
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
