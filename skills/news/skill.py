import requests
import webbrowser

from core import settings
from tts.pyttsx3_tts import SpeakerPyTTSx3

newsapi_access_key = settings.NEWS_API_ACCESS_KEY


def speak_news(text: str) -> None:
    """
    Функция для озвучивания текста новостей.
    """
    speaker = SpeakerPyTTSx3()
    speaker.say(text)
    

def get_news_data(query: str, api_key: str, language='en', max_results=3) -> None:
    url = f"https://newsapi.org/v2/everything?q={query}&language={language}&pageSize={max_results}&sortBy=publishedAt"
    headers = {"Authorization": api_key}
    
    response = requests.get(url, headers=headers)
    data = response.json()

    if "articles" in data and data["articles"]:
        for article in data["articles"]:
            title = article["title"]
            link = article["url"]
            description = article.get("description", "Без описания.")
            print(f"Заголовок: {title}\nОписание: {description}\nСсылка: {link}\n\n")
            webbrowser.open(link)
            result = f"Заголовок: {title}\nОписание: {description}."
            speak_news(result)
        return "."
    else:   
        return "Нет новостей по вашему запросу."



def search_news(*args: tuple, **kwargs: dict) -> str:
    """
    Функция для получения последних новостей по запросу.
    """
    search_query = kwargs.get("phrase", None)

    if not search_query:
        return "Что нужно найти?"
    
    result = get_news_data(search_query, newsapi_access_key, language='ru', max_results=3)
    # Здесь должна быть логика получения новостей, например, через API
    # Для примера вернем статический ответ
    return result

__all__ = ("search_news",)
