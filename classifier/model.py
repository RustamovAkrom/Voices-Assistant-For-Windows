from core.config import config


class IntentClassifier:
    def __init__(self):
       self.commands = config.get_commands()
        
    def classify(self, text: str) -> str:
        text = text.lower()
        for intent, data in self.commands.items():
            for example in data.get('examples', []):
                if example.lower() in text:
                    return intent
        return config.get("classifier", {}).get("fallback_intent", "unknown")
    

classifier = IntentClassifier()
