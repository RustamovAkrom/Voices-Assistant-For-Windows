import sys

# Проверка версии Python
if sys.version_info < (3, 7):
    print("Python 3.7+ is required to run this script. Please upgrade Python to 3.13")
    sys.exit(1)

import time
import string
import random
import re

import skills
from utils.resolve import resolve_attr
from utils.fuzzy_matcher import find_best_match
from core.speakers.silero_tts import SpeakerSileroTTS

# from tts.pyttsx3_tts import SpeakerPyTTSx3
from core.speakers.audio_play import PlayAudio
from core.recognizers.offline import OfflineRecognizer
from core.recognizers.online import OnlineRecognizer
from core.recognizers.porcupine_listener import PorcupineListener
from utils.logger import logger
from core import settings
from core import words_data as words


def clean_query_text(text: str):
    stop_words = {"о", "об", "в", "на", "про", "по", "из", "с", "от", "для", "и", "мне"}
    words = text.strip().split()
    if words and words[0] in stop_words:
        words.pop(0)
    return " ".join(words)


def find_command_from_dataset(user_text: str, dataset: list, threshold: int = 70):
    # original_text = user_text
    user_text = user_text.lower().strip()
    user_text = user_text.translate(str.maketrans("", "", string.punctuation))

    for item in dataset:
        best_match, best_score = find_best_match(user_text, item["phrases"])
        if best_score >= threshold:
            pattern = re.escape(best_match.lower())
            cleaned_text = re.sub(pattern, "", user_text, count=1).strip()
            cleaned_text = clean_query_text(cleaned_text)
            return (
                item.get("handler", None),
                cleaned_text.strip(".|"),
                item.get("text", None),
                item.get("param", False),
            )

    return (None, None, None, False)


def process_command(cmd_text: str) -> None:
    """
    Обрабатывает распознанную команду, ищет соответствующий обработчик
    и вызывает его с параметром, если требуется.
    :param cmd_text: Распознанная команда в виде строки
    """

    logger.debug(f"process_command: cmd_text='{cmd_text}'")
    handler, phrase, text, param_required = find_command_from_dataset(
        cmd_text, words.data_set, 95
    )

    # If handler not found run that code
    if not handler:
        if text:
            logger.info(f"Команда не распознана: {phrase}")
            speaker_silero.say(text)
        else:
            logger.warning(f"Команда не распознана: {cmd_text}")
            print(f"[{cmd_text}] → Команда не распознана и не реализована")
            play_audio.play("not_found")
        return

    # If text already exist it will speak by SileroTTS
    if text:
        logger.info(f"Команда распознана: {phrase} → {handler}")
        speaker_silero.say(text)
    else:
        play_audio.play(random.choice(["ok1", "ok2", "ok3"]))

    try:
        func = resolve_attr(skills, handler)
        logger.debug(f"Resolved handler: {handler} → {func}")

        if param_required:
            # Если требуется параметр, передаем его в функцию
            logger.debug(
                f"Выполнение команды с параметрами: {cmd_text}, phrase={phrase}, text={text}, param_required={param_required}"
            )
            result = func(
                cmd_text,
                handler=handler,
                phrase=phrase,
                text=text,
                param_required=param_required,
            )
        else:
            logger.debug(
                f"Выполнение команды без параметров: {cmd_text}, handler={handler}, phrase={phrase}, text={text}, param_required={param_required}"
            )
            result = func()

        if result:
            speaker_silero.say(result)
            logger.info(f"[{cmd_text}] → Выполнена команда: {result}")
            print(f"[{cmd_text}] → Выполнена команда: {result}")

        else:
            print(f"[{cmd_text}] → Команда выполнена, но нет ответа")

    except Exception as e:
        logger.error(f"[{cmd_text}] → Ошибка при выполнении команды: {e}")
        print(f"[{cmd_text}] → Ошибка при выполнении команды: {e}")
        play_audio.play("not_found")


def splitter_commands(cmd_text: str = None):
    splitters = settings.SPLITTERS
    commands = [cmd_text]
    for splitter in splitters:
        new_commands = []
        for c in commands:
            new_commands.extend([x.strip() for x in c.split(splitter) if x.strip()])
        commands = new_commands
    return commands


def main() -> None:
    logger.info("Jarvis is starting...")
    ACTIVATION_TIMEOUT = 15  # 15 секунд
    play_audio.play(random.choice(["run1", "run2"]))

    active_until = 0

    while True:
        # Если не активен, ждем активационное слово через PorcupineListener
        if time.time() > active_until:
            print(f"Ожидание активационного слова ({settings.PORCUPINE_KEYWORDS})...")

            if porcupine_listener.listen():
                play_audio.play(random.choice(["great1", "great2", "great3"]))

                print("Активация! Jarvis слушает команды 15 секунд...")
                logger.info("Активация Jarvis через PorcupineListener")
                active_until = time.time() + ACTIVATION_TIMEOUT

            continue

        # Активен: слушаем команду через OfflineRecognizer
        print("Jarvis активен. Ожидание команды...")

        cmd_text = recognizer.listen().lower()

        print(f"Recognized command: {cmd_text}")
        logger.debug(f"Recognized command: {cmd_text}")

        if not cmd_text:
            print("Команда не распознана, повторите.")
            logger.warning("Команда не распознана, повторите.")
            continue

        # Split commands which talked user
        commands = splitter_commands(cmd_text)

        for single_cmd in commands:
            trg = settings.TRIGGERS.intersection(single_cmd.split())
            if trg:
                play_audio.play(random.choice(["great1", "great2", "great3"]))
                print("Активация продлена! Jarvis слушает еще 15 секунд...")
                logger.info(f"Команда активирована триггером: {trg}")
                active_until = time.time() + ACTIVATION_TIMEOUT
                cmd = single_cmd
                for t in trg:
                    cmd = cmd.replace(t, "").strip()
                if cmd:
                    logger.debug(f"Команда после триггера: {cmd}")
                    process_command(cmd)
                continue
            logger.debug(f"Обработка команды: {single_cmd}")
            process_command(single_cmd)
        # После первой активации Jarvis всегда слушает команды, не сбрасывая active_until
        active_until = time.time() + ACTIVATION_TIMEOUT


if __name__ == "__main__":
    print("Initializing...")
    logger.info("Initializing...")

    # Инициализация компонентов
    porcupine_listener = PorcupineListener(
        keywords=settings.PORCUPINE_KEYWORDS, access_key=settings.PORCUPINE_ACCESS_KEY
    )
    speaker_silero = SpeakerSileroTTS(settings.SILERO_TTS_SPEAKER)
    play_audio = PlayAudio(settings.AUDIO_FILES)
    recognizer = (
        OnlineRecognizer()
        if settings.USE_ONLINE_RECOGNIZER
        else OfflineRecognizer(settings.VOSK_MODEL_PATH)
    )

    print(
        "Initialization complete. Jarvis is ready to listen.\n"
        "Press Ctrl+C to stop.\n"
    )

    try:
        main()
    except KeyboardInterrupt or Exception as e:
        print(f"Остановлено пользователем. {e}")
        porcupine_listener.close()
        logger.info("Jarvis stopped by user.")
        sys.exit(0)
