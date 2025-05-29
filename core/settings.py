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


# Default speaker for the Silero TTS (Text-to-Speech) engine
SILERO_TTS_SPEAKER = "aidar" # Default speaker for Silero TTS example: "aidar", "baya", "jane", "omaz", "xenia"

# Directory where the applications are located
# This dictionary maps application names to their executable paths
APPS_DIR = {
    ("телеграм", "telegram"): "Telegram.exe",
    ("блокнот", "ноутпад", "notepad"): "notepad.exe",
    ("гугл", "chrome", "хром"): "chrome.exe",
    ("vs", "vscode", "вс код"): "Code.exe",
}
