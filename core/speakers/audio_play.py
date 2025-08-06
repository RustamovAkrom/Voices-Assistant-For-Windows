import sounddevice as sd
import soundfile as sf


class PlayAudio:
    def __init__(self, audio_files: dict):
        self.audio_files = audio_files

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
