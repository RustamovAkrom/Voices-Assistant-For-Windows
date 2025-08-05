import os
from dotenv import load_dotenv, find_dotenv

# Load environment veribles from .env file
load_dotenv(find_dotenv(".env"))

# Activation settings for Porcupine wake word detection
PORCUPINE_KEYWORDS = ("jarvis",)

 # If you want voices recognitions detect online, you would replace value to `True`
ONLINE_VOICE_RECOGNIZER_IS_ACTIVE = False

TRIGGERS = {
    "джарвис",
    "djarvis",
    "чарльз",
}

VOSK_MODEL_PATH = "data/models/vosk"

# Access key for Porcupine wake word detection
# You will must get access key from Picovoice Console in site https://console.picovoice.ai/
PORCUPINE_ACCESS_KEY = os.getenv("PORCUPINE_ACCESS_KEY")

# Access key for NewsAPI
# You will must get access key from NewsAPI in site https://newsapi.org/
NEWS_API_ACCESS_KEY = os.getenv("NEWS_API_ACCESS_KEY")

# Path to the directory where the audio files are stored
LOGGER_FILE = "asistent.log"
LOGGER_ACTIVE = False
LOGGER_FILE_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Default speaker for the Silero TTS (Text-to-Speech) engine
SILERO_TTS_SPEAKER = "aidar"  # Default speaker for Silero TTS example: "aidar", "baya", "jane", "omaz", "xenia"

# Auto play audo files settings please do not tuch
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