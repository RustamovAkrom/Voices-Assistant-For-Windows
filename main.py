import sys
# Проверка версии Python
if sys.version_info < (3, 7):
    print("Python 3.7+ is required to run this script.")
    sys.exit(1)

import time
import string
import random

import skills
from utils.resolve import resolve_attr
from tts.silero_tts import Speaker
from tts.audio_play import PlayAudio
from recognizer.offline import OfflineRecognizer
from recognizer.porcupine_listener import PorcupineListener
from core.logger import logger
from core import settings
from core import words_data as words

from Levenshtein import distance as levenshtein_distance
from typing import Optional, Tuple


def find_command(
    user_text: str, 
    dataset: list, 
    threshold: int = 3
    
) -> Tuple[Optional[str], Optional[str], Optional[str], bool]:
    """
    Ищет команду в пользовательском тексте, используя fuzzy matching.
    Возвращает: (handler, phrase, text, param_required)
    """
    user_text = user_text.lower().strip()
    user_text = user_text.translate(str.maketrans('', '', string.punctuation))

    best = (None, None, None, None)
    min_dist = threshold + 1

    for item in dataset:
        for phrase in item['phrases']:
            phrase_clean = phrase.lower().strip()
            dist = levenshtein_distance(user_text, phrase_clean)
            if dist < min_dist:
                min_dist = dist
                best = (
                    item.get('handler'),
                    phrase,
                    item.get("text", None),
                    item.get('param', False)
                )
            # Точное вхождение фразы в текст пользователя (без Левенштейна)
            if phrase_clean in user_text:
                return (
                    item.get('handler'),
                    phrase,
                    item.get("text", None),
                    item.get('param', False)
                )

    if min_dist <= threshold:
        return best

    return None, None, None, None


def process_command(cmd_text: str) -> None:
    """
    Обрабатывает распознанную команду, ищет соответствующий обработчик
    и вызывает его с параметром, если требуется.
    :param cmd_text: Распознанная команда в виде строки
    """

    logger.debug(f"process_command: cmd_text='{cmd_text}'")
    handler, phrase, text, param_required = find_command(cmd_text, words.data_set)

    if not handler:
        if text:
            logger.info(f"Команда не распознана: {phrase}")
            speaker.say(text)
        else:
            logger.warning(f"Команда не распознана: {cmd_text}")
            print(f"[{cmd_text}] → Команда не распознана и не реализована")
            play_audio.play("not_found")
        return

    if text:
        logger.info(f"Команда распознана: {phrase} → {handler}")
        speaker.say(text)
    else:
        play_audio.play(random.choice(['ok1', 'ok2', 'ok3']))

    try:
        func = resolve_attr(skills, handler)
        logger.debug(f"Resolved handler: {handler} → {func}")

        if param_required:
            # Если требуется параметр, передаем его в функцию
            logger.debug(f"Выполнение команды с параметрами: {cmd_text}, phrase={phrase}, text={text}, param_required={param_required}")
            result = func(cmd_text, handler=handler, phrase=phrase, text=text, param_required=param_required)
        else:
            logger.debug(f"Выполнение команды без параметров: {cmd_text}, handler={handler}, phrase={phrase}, text={text}, param_required={param_required}")
            result = func()

        if result:
            speaker.say(result)
            logger.info(f"[{cmd_text}] → Выполнена команда: {result}")
            print(f"[{cmd_text}] → Выполнена команда: {result}")

        else:
            print(f"[{cmd_text}] → Команда выполнена, но нет ответа")

    except Exception as e:
        logger.error(f"[{cmd_text}] → Ошибка при выполнении команды: {e}")
        print(f"[{cmd_text}] → Ошибка при выполнении команды: {e}")
        play_audio.play("not_found")


def main() -> None:
    logger.info("Jarvis is starting...")
    ACTIVATION_TIMEOUT = 15  # 15 секунд
    play_audio.play(random.choice(['run1', 'run2']))

    active_until = 0

    while True:
        # Если не активен, ждем активационное слово через PorcupineListener
        if time.time() > active_until:
            print("Ожидание активационного слова (Porcupine)...")

            if porcupine_listener.listen():
                play_audio.play(random.choice(['great1', 'great2', 'great3']))

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

        # Разделяем на несколько команд по разделителям (точка, запятая, 'и', 'затем')
        splitters = [".", ",", " и ", " затем "]
        commands = [cmd_text]
        for splitter in splitters:
            new_commands = []
            for c in commands:
                new_commands.extend([x.strip() for x in c.split(splitter) if x.strip()])
            commands = new_commands

        for single_cmd in commands:
            trg = settings.TRIGGERS.intersection(single_cmd.split())
            if trg:
                play_audio.play(random.choice(['ok1', 'ok2', 'ok3']))
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
    
    porcupine_listener = PorcupineListener(keywords=settings.PORCUPINE_KEYWORDS, access_key=settings.PORCUPINE_ACCESS_KEY)
    recognizer = OfflineRecognizer(settings.VOSK_MODEL_PATH)
    speaker = Speaker()
    speaker.speaker = settings.SILERO_TTS_SPEAKER
    play_audio = PlayAudio()

    print("Initialization complete. Jarvis is ready to listen.")
    print("Press Ctrl+C to stop.")

    try:
        main()
    except KeyboardInterrupt or Exception as e:
        print(f"Остановлено пользователем. {e}")
        porcupine_listener.close()
        logger.info("Jarvis stopped by user.")
        sys.exit(0)
