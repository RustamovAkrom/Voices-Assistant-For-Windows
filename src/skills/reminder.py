import time
import threading
import pyttsx3

def set_timer(seconds):
    def timer_thread():
        time.sleep(seconds)
        engine = pyttsx3.init()
        engine.say("Таймер завершён!")
        engine.runAndWait()
    threading.Thread(target=timer_thread, daemon=True).start()
    return f"Таймер на {seconds} секунд установлен."


def set_reminder(text, delay_seconds):
    def reminder_thread():
        time.sleep(delay_seconds)
        engine = pyttsx3.init()
        engine.say(f"Напоминание: {text}")
        engine.runAndWait()
    threading.Thread(target=reminder_thread, daemon=True).start()
    return f"Напоминание установлено: {text}"
