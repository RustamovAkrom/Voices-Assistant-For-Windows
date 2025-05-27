import words
import string
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

if __name__ == "__main__":
    examples = [
        " asdfadf asdf здравствуй asdf asd fas df ads fad f",
        "здравствуй!",
        "здравстуй",  # опечатка
        "привет",
        "asdf доброе утро мой друг",
        "включи музыку",
        "выключи свет"
    ]
    for text in examples:
        handler, phrase, param = find_command(text, words.data_set)
        if handler:
            print(f"Фраза: '{text}' → Обработчик: {handler} (ключевое слово: '{phrase}', param: {param})")
        else:
            print(f"Фраза: '{text}' → Команда не распознана")