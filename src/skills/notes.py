from pathlib import Path

NOTES_FILE = Path("data/notes.txt")

def add_note(note):
    NOTES_FILE.parent.mkdir(exist_ok=True)
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(note + "\n")
    return "Заметка добавлена."

def read_notes():
    if not NOTES_FILE.exists():
        return "Заметок пока нет."
    with open(NOTES_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()

def clear_notes():
    if NOTES_FILE.exists():
        NOTES_FILE.unlink()
        return "Все заметки удалены."
    return "Нет заметок для удаления."
