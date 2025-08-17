from datetime import datetime
from utils.decorators import log_command, timeit


@log_command("default.date_time.data_speaker.say_data")
@timeit()
def say_date(*args: tuple, **kwargs: dict):
    """
    Функция для получения текущего времени по команде.
    :param args: Дополнительные аргументы (не используются)
    :return: Строка с текущим временем
    """
    speaker_pyttsx3 = kwargs.get("speaker_pyttsx3", None)

    if not speaker_pyttsx3:
        print("Error speaker PyTTSx3 not found")
    
    date_object = datetime.date(datetime.now())
    current_day = date_object.day
    current_month = date_object.month
    current_year = date_object.year

    date_text = f"день: {current_day}, месяц: {current_month}, год: {current_year}"
    speaker_pyttsx3.say(f"сегодня дата: {date_text}")
