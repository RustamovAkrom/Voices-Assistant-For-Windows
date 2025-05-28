import os
# Settings for the Jarvis application
# Activation settings for Porcupine wake word detection
PORCUPINE_KEYWORDS = ("jarvis", )

VOSK_MODEL_PATH = "data/models/vosk"

# Access key for Porcupine wake word detection
# You will must get access key from Picovoice Console in site https://console.picovoice.ai/
PORCUPINE_ACCESS_KEY = os.getenv("PORCUPINE_ACCESS_KEY")

# Path to the directory where the audio files are stored
LOGGER_FILE = "asistent.log"