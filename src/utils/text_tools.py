import re

STOP_WORDS = ["пожалуйста", "можешь", "давай", "а", "или"]

def clean_text(text: str) -> str:
    text = text.lower()
    for word in STOP_WORDS:
        text = text.replace(word, "")
    return text.strip()

def split_commands(text: str) -> list[str]:
    text = clean_text(text)
    return re.split(r"\s*(?:и|а|или)\s*", text)