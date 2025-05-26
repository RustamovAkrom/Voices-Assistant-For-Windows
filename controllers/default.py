# controllers/handlers.py

def reply_here():
    return "Да, я здесь."

def reply_greeting():
    return "Приветствую! Чем могу помочь?"

def reply_howareyou():
    return "У меня всё хорошо!"

def reply_skills():
    return "Я могу рассказать погоду, время, новости, анекдот, включить музыку, свет и многое другое."

def reply_joke():
    return "Вот анекдот: — Почему программисты путают Новый год с Хэллоуином? — Потому что 31 OCT = 25 DEC."

def get_news():
    return "Последние новости: ... (здесь может быть интеграция с API новостей)"

def get_location():
    return "Ваше местоположение: ... (здесь может быть интеграция с геолокацией)"

def turn_on_light():
    return "Включаю свет. (интеграция с умным домом)"

def turn_off_light():
    return "Выключаю свет. (интеграция с умным домом)"

def play_music():
    return "Включаю музыку. (интеграция с плеером)"

def stop_music():
    return "Останавливаю музыку. (интеграция с плеером)"
