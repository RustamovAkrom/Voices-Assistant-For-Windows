from datetime import datetime

def get_time():
    return datetime.now().strftime("Сейчас %H:%M")

def get_date():
    return datetime.now().strftime("Сегодня %d %B %Y года")
