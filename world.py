import queue
import sounddevice as sd
import vosk
import json
import words
import time
from recognizer.offline import OfflineRecognizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from tts.silero_tts import Speaker
from tts.audio_play import PlayAudio


def recognize(data, vectorizer, clf):
    # Разбиваем входной текст на предложения/команды (по запятым, "и", точкам)
    import re
    commands = re.split(r'[,.!?;]|\s+и\s+', data)
    commands = [cmd.strip() for cmd in commands if cmd.strip()]

    from controllers import handlers
    from controllers import weather, time_service, music

    handlers_dict = {
        "reply_here": handlers.reply_here,
        "reply_greeting": handlers.reply_greeting,
        "reply_howareyou": handlers.reply_howareyou,
        "reply_skills": handlers.reply_skills,
        "reply_joke": handlers.reply_joke,
        "get_news": handlers.get_news,
        "get_location": handlers.get_location,
        "turn_on_light": handlers.turn_on_light,
        "turn_off_light": handlers.turn_off_light,
        "play_music": handlers.play_music,
        "stop_music": handlers.stop_music,
        "get_weather": weather.get_weather,
        "get_time": time_service.get_time,
        "get_music": music.get_music,
    }

    for cmd in commands:
        text_vector = vectorizer.transform([cmd]).toarray()[0]
        func_name = clf.predict([text_vector])[0]
        handler = handlers_dict.get(func_name)
        if handler:
            result = handler()
            print(f"[{cmd}] → {result}")
            speaker.say(result)
        else:
            print(f"[{cmd}] → Команда не реализована")


def traning_data(data_set:dict):
    # Подготовка обучающих данных
    X = []
    y = []
    for phrases, answer in words.data_set.items():
        for phrase in phrases:
            X.append(phrase)
            y.append(answer)

    vectorizer = CountVectorizer()
    vectors = vectorizer.fit_transform(X)

    clf = LogisticRegression()
    clf.fit(vectors, y)

    return vectorizer, clf


def main():
    vectorizer, clf = traning_data(words.data_set)

    start_time = time.time() - 1000
    play_audio.play("run")

    while True:
        print("Ожидание активационного слова...")
        text = recognizer.listen().lower()
        print(f"Recognized text: {text}")

        trg = words.TRIGGERS.intersection(text.split())
        
        if trg:
            play_audio.play("great")
            
            print("Активация! Jarvis слушает команды 15 секунд...")
            start_time = time.time()

            removed_trg_command = text.replace(" ".join(trg), "").strip()
            # Если активационное слово распознано, обрабатываем его
            recognize(removed_trg_command, vectorizer, clf)

            # Слушаем команды в течение 15 секунд
            while (time.time() - start_time) <= 15:

                cmd_text = recognizer.listen()
                print(f"Recognized command: {cmd_text}")

                if cmd_text:
                    # Мгновенно реагируем на повторное активационное слово
                    if any(t in cmd_text.split() for t in words.TRIGGERS):
                        play_audio.play("great")
                        # НЕ продолжаем, а сразу сбрасываем таймер и слушаем новые команды
                        start_time = time.time()
                        continue
                    recognize(cmd_text, vectorizer, clf)
                else:
                    print("Команда не распознана, повторите.")                


if __name__ == "__main__":
    print("Initializing...")

    recognizer = OfflineRecognizer()
    speaker = Speaker()
    play_audio = PlayAudio()

    main()
