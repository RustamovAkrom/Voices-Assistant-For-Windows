import words
import time
from recognizer.offline import OfflineRecognizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from tts.silero_tts import Speaker
from tts.audio_play import PlayAudio
from utils.resolve import resolve_attr


def recognize(data, vectorizer, clf):
    import skills

    # Обработка распознанной команды
    text_vector = vectorizer.transform([data]).toarray()[0]
    func_name = clf.predict([text_vector])[0]
    print(func_name)
    if func_name:
        try:
            result = resolve_attr(skills, func_name)(data)
            speaker.say(result)
            print(f"[{data}] → Выполнена команда: {result}")
        except Exception as e:
            print(f"[{data}] → Ошибка при выполнении команды: {e}")
            play_audio.play("not_found")
    else:
        print(f"[{data}] → Команда не реализована")


def traning_data(data_set:dict):
    # Подготовка обучающих данных
    X = []
    y = []
    for phrases, answer in data_set.items():
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
