def get_time(*args):
    """
    Функция для получения текущего времени по команде.
    :param args: Дополнительные аргументы (не используются)
    :return: Строка с текущим временем
    """
    from datetime import datetime

    current_time = datetime.now().strftime("%H:%M:%S")
    return (
        f"Текущее время: {current_time}"  # Возвращаем текущее время в формате ЧЧ:ММ:СС.
    )
