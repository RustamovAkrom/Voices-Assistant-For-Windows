import wikipedia
import webbrowser

wikipedia.set_lang("ru")


def search_wiki(*args: tuple, **kwargs: dict) -> str:
    search_query = kwargs.get("phrase", None)

    if not search_query:
        return "Что нужно найти?"
    
    try:
        summary = wikipedia.summary(search_query, sentences=2)
        return f"Вот что я нашел: {summary}"
    
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Найдено несколько вариантов: {e.options}. Пожалуйста, уточните запрос."
    
    except wikipedia.exceptions.PageError:
        search_url = f"https://google.com/search?q={search_query}"
        webbrowser.open(search_url)
        return "Я не нашел информации по вашему запросу. Открыл Google для поиска."
    
    except Exception as e:
        return f"Произошла ошибка при поиске: {str(e)}"
