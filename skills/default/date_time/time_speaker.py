from datetime import datetime
from utils.decorators import log_command, timeit


@log_command("default.date_time.time_speaker.say_time")
@timeit()
def say_time(*args: tuple, **kwargs: dict):
    """
    Функция для получения текущего времени по команде.
    :param args: Дополнительные аргументы (не используются)
    :return: Строка с текущим временем
    """
    speaker_pyttsx3 = kwargs.get("speaker_pyttsx3", None)

    if not speaker_pyttsx3:
        print("Error speaker PyTTSx3 not found")
    
    current_time = datetime.now().strftime("%H:%M:%S")
    speaker_pyttsx3.say(f"сегодня время: {current_time}")
