import sys
# Проверка версии Python
if sys.version_info < (3, 7):
    print("Python 3.7+ is required to run this script.")
    sys.exit(1)

import time
import string

import skills
from utils.resolve import resolve_attr
from tts.silero_tts import Speaker
from tts.audio_play import PlayAudio
from recognizer.offline import OfflineRecognizer
from recognizer.porcupine_listener import PorcupineListener
from core import settings
from core import words_data as words

from Levenshtein import distance as levenshtein_distance


def find_command(user_text, dataset, threshold=3) -> tuple[str|None, str:None, str|None, bool]:
    """
    Ищет команду в пользовательском тексте, используя расстояние Левенштейна.
    :param user_text: Текст команды, введенный пользователем
    :param dataset: Список команд с фразами и обработчиками
    :param threshold: Максимальное расстояние Левенштейна для совпадения
    :return: Кортеж из обработчика команды, распознанной фразы и параметра (если требуется)
    """

    # threshold — максимальное расстояние Левенштейна для совпадения
    user_text = user_text.lower().strip()
    # Удаляем пунктуацию из текста пользователя
    user_text = user_text.translate(str.maketrans('', '', string.punctuation))
    # Собираем все фразы из датасета в один список
    # и приводим их к нижнему регистру
    all_phrases = [phrase.lower().strip() for item in dataset for phrase in item['phrases']]
    # Ищем наилучшее совпадение по расстоянию Левенштейна
    best_phrase = None
    best_dist = None
    for phrase in all_phrases:
        dist = levenshtein_distance(user_text, phrase)
        if best_dist is None or dist < best_dist:
            best_dist = dist
            best_phrase = phrase
    # Если нашли подходящее совпадение, проверяем его в датасете
    # и возвращаем соответствующий обработчик
    # и фразу, если расстояние меньше порога
    # и параметр, если он есть
    if best_phrase is not None and best_dist is not None and best_dist <= threshold:
        for item in dataset:
            for p in item['phrases']:
                if best_phrase == p.lower().strip():
                    return item.get('handler'), p, item.get("text", None), item.get('param', False)
    # Если не нашли подходящее совпадение, ищем, есть ли хотя бы одно слово из команд в пользовательской фразе
    # Если не нашли — ищем, есть ли хотя бы одно слово из команд в пользовательской фразе
    for item in dataset:
        for phrase in item['phrases']:
            if phrase.lower().strip() in user_text:
                return item.get('handler'), phrase, item.get("text", None), item.get('param', False)
    # Если ничего не нашли, возвращаем None
    return None, None, None, None


def process_command(cmd_text: str) -> None:
    """
    Обрабатывает распознанную команду, ищет соответствующий обработчик
    и вызывает его с параметром, если требуется.
    :param cmd_text: Распознанная команда в виде строки
    """

    handler, phrase, text, param_required = find_command(cmd_text, words.data_set)

    if handler:
        if text:
            # Если есть текст для произнесения, озвучиваем его
            speaker.say(text)
        else:
            play_audio.play("ok")
        try:

            if param_required:
                # Если команда требует параметр, передаем весь текст без фразы
                query = cmd_text.replace(phrase, '').strip()
                # Если после удаления фразы ничего не осталось, задаем дефолтный запрос
                if not query:
                    query = "запрос не распознан"
                
                # Вызываем обработчик с параметром
                result = resolve_attr(skills, handler)(query)

            else:
                # Если команда не требует параметр, просто вызываем обработчик
                result = resolve_attr(skills, handler)()

            if result:
                # Если результат не пустой, произносим его
                speaker.say(result)
                print(f"[{cmd_text}] → Выполнена команда: {result}")

            else:
                print(f"[{cmd_text}] → Команда выполнена, но нет ответа")

        except Exception as e:
            print(f"[{cmd_text}] → Ошибка при выполнении команды: {e}")
            play_audio.play("not_found")
    else:
        if text:
            speaker.say(text)
        else:
            print(f"[{cmd_text}] → Команда не распознана и не реализована")
            play_audio.play("not_found")


def main() -> None:
    ACTIVATION_TIMEOUT = 900  # 15 минут
    play_audio.play("run")

    active_until = 0

    while True:
        # Если не активен, ждем активационное слово через PorcupineListener
        if time.time() > active_until:
            print("Ожидание активационного слова (Porcupine)...")
            if porcupine_listener.listen():
                play_audio.play("great")
                print("Активация! Jarvis слушает команды 15 минут...")
                active_until = time.time() + ACTIVATION_TIMEOUT
            continue

        # Активен: слушаем команду через OfflineRecognizer
        print("Jarvis активен. Ожидание команды...")
        cmd_text = recognizer.listen().lower()
        print(f"Recognized command: {cmd_text}")

        if not cmd_text:
            print("Команда не распознана, повторите.")
            continue

        trg = words.TRIGGERS.intersection(cmd_text.split())
        if trg:
            play_audio.play("great")
            print("Активация продлена! Jarvis слушает еще 15 минут...")
            active_until = time.time() + ACTIVATION_TIMEOUT
            # Если вместе с триггером есть команда — выполнить её
            cmd = cmd_text
            for t in trg:
                cmd = cmd.replace(t, "").strip()
            if cmd:
                process_command(cmd)
            continue

        # Обычная команда
        process_command(cmd_text)
        active_until = time.time() + ACTIVATION_TIMEOUT


if __name__ == "__main__":
    print("Initializing...")
    
    porcupine_listener = PorcupineListener(keywords=settings.PORCUPINE_KEYWORDS, access_key=settings.PORCUPINE_ACCESS_KEY)
    recognizer = OfflineRecognizer()
    speaker = Speaker()
    play_audio = PlayAudio()

    try:
        main()
    except KeyboardInterrupt or Exception as e:
        print(f"Остановлено пользователем. {e}")
        porcupine_listener.close()
        sys.exit(0)
    
