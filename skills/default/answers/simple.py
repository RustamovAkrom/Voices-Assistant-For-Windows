# skills/default/answers/simple.py
import random


def simple_answer(*args: tuple, **kwargs: dict) -> None:
    responses = [
        "Привет! Как я могу помочь?",
        "Здравствуйте! Чем могу быть полезен?",
        "Доброе утро! Как настроение?",
        "Добрый день! Что вас интересует?",
        "Добрый вечер! Как прошел ваш деiнь?",
        "Приветик! Что нового у вас?",
        "Приветствую! Как дела?",
        "Здарова! Чем могу помочь?",
        "Хай! Что интересного хотите узнать?",
        "Добрейшего времени суток! Как я могу помочь?",
    ]
    speaker_silero = kwargs.get("speaker_silero", None)
    if not speaker_silero:
        print("Silero Speaker Not Found")
        return
    speaker_silero.say(random.choice(responses))


def thanks_answer(*args: tuple, **kwargs: dict) -> None:
    play_audio = kwargs.get("play_audio", None)

    if not play_audio:
        print("Play Audio not found")

    play_audio.play("thanks")
