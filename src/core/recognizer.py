class Recognizer:
    def __init__(self, config):
        self.config = config

    def listen_text(self):
        text = input("🗣️ Say command (or type): ").strip().lower()
        return text
