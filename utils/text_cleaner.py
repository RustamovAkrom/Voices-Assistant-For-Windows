def clean_text(text):
    trash_words = [
        "пожалуйста",
        "если можно",
        "можешь ли",
        "а не мог бы ты",
        "сделай",
        "давай",
        "можешь",
        "покажи",
    ]
    for word in trash_words:
        text = text.replace(word, "")
    return text.strip().lower()
