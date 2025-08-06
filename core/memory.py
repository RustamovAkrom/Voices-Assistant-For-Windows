class MemoryManager:
    def __init__(self):
        self.history = []

    def remember(self, text: str):
        self.history.append(text)

    def get_history(self) -> list[str]:
        return self.history

    def clear_history(self):
        self.history.clear()
