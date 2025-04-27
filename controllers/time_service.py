from datetime import datetime
import time


def get_time() -> str:
    """
    Возвращает текущее время в формате 'HH:MM:SS'.
    """
    return datetime.now().strftime("%H:%M:%S")


def set_timer(seconds_str: str) -> None:
    """
    Устанавливает таймер на указанное время.
    :param duration: Время в формате 'HH:MM'.
    """

    try:
        seconds = int(seconds_str)
        print(f"Таймер на {seconds} секунд запущен.")
        time.sleep(seconds)
        print("Время вышло!")
    except ValueError:
        print("Неверное число секунд.")
