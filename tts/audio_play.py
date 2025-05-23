import sounddevice as sd
import soundfile as sf
import random


class PlayAudio:
    def __init__(self):
        self.base_path = r"data\media\audios"
        self.audio_files = {
            "great": fr"{self.base_path}\jarvis-og_greet{random.randint(1, 3)}.wav",
            "not_found": fr"{self.base_path}\jarvis-og_not_found.wav",
            "off": fr"{self.base_path}\jarvis-og_off.wav",
            "run": fr"{self.base_path}\jarvis-og_run.wav",
            "stupid": fr"{self.base_path}\jarvis-og_stupid.wav",
            "ok": fr"{self.base_path}\jarvis-og_ok{random.randint(1, 4)}.wav",
            "thanks": fr"{self.base_path}\jarvis-og_thanks.wav",
        }
    
    def play(self, name: str):
        match name:
            case "great":
                file_path = self.audio_files["great"]
            case "not_found":
                file_path = self.audio_files["not_found"]
            case "off":
                file_path = self.audio_files["off"]
            case "run":
                file_path = self.audio_files["run"]
            case "stupid":
                file_path = self.audio_files["stupid"]
            case "ok":
                file_path = self.audio_files["ok"]
            case "thanks":
                file_path = self.audio_files["thanks"]

        self.play_audio(file_path)

    def play_audio(self, file_path: str):
        data, samplerate = sf.read(file_path)
        sd.play(data, samplerate)
        sd.wait()