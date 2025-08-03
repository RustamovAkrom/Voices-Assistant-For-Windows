import os
from dotenv import load_dotenv

load_dotenv()
# Settings for the Jarvis application
# Activation settings for Porcupine wake word detection
PORCUPINE_KEYWORDS = ("jarvis", )

TRIGGERS = {"джарвис", "djarvis", "чарльз", }

VOSK_MODEL_PATH = "data/models/vosk"

# Access key for Porcupine wake word detection
# You will must get access key from Picovoice Console in site https://console.picovoice.ai/
PORCUPINE_ACCESS_KEY = os.getenv("PORCUPINE_ACCESS_KEY")

# Path to the directory where the audio files are stored
LOGGER_FILE = "asistent.log"
LOGGER_ACTIVE = False

# Default speaker for the Silero TTS (Text-to-Speech) engine
SILERO_TTS_SPEAKER = "aidar" # Default speaker for Silero TTS example: "aidar", "baya", "jane", "omaz", "xenia"

