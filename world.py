import string
import time
import words

from utils.resolve import resolve_attr
from tts.silero_tts import Speaker
from tts.audio_play import PlayAudio
from recognizer.offline import OfflineRecognizer

from Levenshtein import distance as levenshtein_distance


def find_command(user_text, dataset, threshold=3):
    # threshold — максимальное расстояние Левенштейна для совпадения
    user_text = user_text.lower().strip()
    user_text = user_text.translate(str.maketrans('', '', string.punctuation))
    all_phrases = [phrase.lower().strip() for item in dataset for phrase in item['phrases']]
    best_phrase = None
    best_dist = None
    for phrase in all_phrases:
        dist = levenshtein_distance(user_text, phrase)
        if best_dist is None or dist < best_dist:
            best_dist = dist
            best_phrase = phrase
    if best_phrase is not None and best_dist is not None and best_dist <= threshold:
        for item in dataset:
            for p in item['phrases']:
                if best_phrase == p.lower().strip():
                    return item['handler'], p, item.get('param', False)
    # Если не нашли — ищем, есть ли хотя бы одно слово из команд в пользовательской фразе
    for item in dataset:
        for phrase in item['phrases']:
            if phrase.lower().strip() in user_text:
                return item['handler'], phrase, item.get('param', False)
    return None, None, None


def recognize(data: str):
    import skills

    # Обработка распознанной команды
    handler, phrase, param_required = find_command(data, words.data_set)
    print(handler, phrase, param_required)

    if handler:
        try:
            if param_required:
                # Если команда требует параметр, передаем весь текст
                query = data.replace(phrase, '').strip()
                if not query:
                    query = "запрос не распознан"
                result = resolve_attr(skills, handler)(query)
            else:
                result = resolve_attr(skills, handler)()

            if result:
                speaker.say(result)
                print(f"[{data}] → Выполнена команда: {result}")
            else:
                print(f"[{data}] → Команда выполнена, но нет ответа")
                
        except Exception as e:
            print(f"[{data}] → Ошибка при выполнении команды: {e}")
            play_audio.play("not_found")
    else:
        print(f"[{data}] → Команда не распознана и не реализована")

# def recognize(data: str, vectorizer, clf, dataset: dict):
#     import skills

#     # Обработка распознанной команды
#     text_vector = vectorizer.transform([data]).toarray()[0]
#     func_name = clf.predict([text_vector])[0]

#     entry = next((item for item in dataset if item['handler'] == func_name), None)
#     if entry:
#         if entry.get('param', False):
#             # Если команда требует параметр, передаем весь текст
#             query = data
#             for kw in entry['phrases']:
#                 query = query.replace(kw, '')
#             query = query.strip()
#             if not query:
#                 query = "запрос не распознан"

#             try:
#                 result = resolve_attr(skills, func_name)(query)
#                 if result:
#                     speaker.say(result)
#                     print(f"[{data}] → Выполнена команда: {result}")
#             except Exception as e:
#                 print(f"[{data}] → Ошибка при выполнении команды: {e}")
#                 play_audio.play("not_found")
#         else:
#             try:
#                 result = resolve_attr(skills, func_name)()
#                 if result:
#                     speaker.say(result)
#                     print(f"[{data}] → Выполнена команда: {result}")
#             except Exception as e:
#                 print(f"[{data}] → Ошибка при выполнении команды: {e}")
#                 play_audio.play("not_found")
    # else:
        
    #     # Fuzzy matching для поиска похожих команд
    #     all_phrases = []
    #     handler_map = {}
    #     for item in dataset:
    #         for phrase in item['phrases']:
    #             all_phrases.append(phrase)
    #             handler_map[phrase] = item['handler']
    #     close_matches = get_close_matches(data, all_phrases, n=1, cutoff=0.6)
    #     if close_matches:
    #         closest_phrase = close_matches[0]
    #         func_name = handler_map[closest_phrase]
    #         print(f"[{data}] → Похоже на: {closest_phrase} → Выполняем команду: {func_name}")
    #         recognize(closest_phrase, vectorizer, clf, dataset)
    #     else:
    #         print(f"[{data}] → Команда не распознана и не реализована")

# def recognize(data, vectorizer, clf):
#     import skills

#     # Обработка распознанной команды
#     text_vector = vectorizer.transform([data]).toarray()[0]
#     func_name = clf.predict([text_vector])[0]

#     if func_name:
#         try:
#             result = resolve_attr(skills, func_name)(data)
#             if result:
#                 speaker.say(result)
#                 print(f"[{data}] → Выполнена команда: {result}")
#             else:
#                 print(f"[{data}] → Команда выполнена, но нет ответа")
                
#         except Exception as e:
#             print(f"[{data}] → Ошибка при выполнении команды: {e}")
#             play_audio.play("not_found")
#     else:
#         print(f"[{data}] → Команда не реализована")


# def traning_data(data_set:dict):
#     # Подготовка обучающих данных
#     X = []
#     y = []
#     for phrases, answer in data_set.items():
#         for phrase in phrases:
#             X.append(phrase)
#             y.append(answer)

#     vectorizer = CountVectorizer()
#     vectors = vectorizer.fit_transform(X)

#     clf = LogisticRegression()
#     clf.fit(vectors, y)

#     return vectorizer, clf

# def traning_data(data_set: list):
#     # Подготовка обучающих данных
#     X = []
#     y = []
#     for entry in data_set:
#         phrases = entry['phrases']
#         handler = entry['handler']
#         for phrase in phrases:
#             X.append(phrase)
#             y.append(handler)

#     vectorizer = CountVectorizer(ngram_range=(1, 2))
#     vectors = vectorizer.fit_transform(X)

#     clf = LogisticRegression()
#     clf.fit(vectors, y)

#     return vectorizer, clf


def main():
    # vectorizer, clf = traning_data(words.data_set)

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

            # removed_trg_command = text.replace(" ".join(trg), "").strip()
            # Если активационное слово распознано, обрабатываем его
            # recognize(removed_trg_command, vectorizer, clf, words.data_set)

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
                    recognize(cmd_text)
                    # recognize(cmd_text, vectorizer, clf, words.data_set)
                else:
                    print("Команда не распознана, повторите.")                


if __name__ == "__main__":
    print("Initializing...")

    recognizer = OfflineRecognizer()
    speaker = Speaker()
    play_audio = PlayAudio()

    main()
