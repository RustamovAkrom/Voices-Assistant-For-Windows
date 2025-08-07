import wikipedia
import webbrowser

wikipedia.set_lang("ru")


def search_wiki(*args: tuple, **kwargs: dict) -> str:
    search_query = kwargs.get("phrase", None)
    speaker_silero = kwargs.get("speaker_silero", None)

    if not search_query:
        return "Что нужно найти?"
    
    if not speaker_silero:
        return "Error speaker Silero not found"

    try:
        summary = wikipedia.summary(search_query, sentences=2)
        speaker_silero.say(f"Вот что я нашел: {summary}")

    except wikipedia.exceptions.DisambiguationError as e:
        speaker_silero.say(f"Найдено несколько вариантов: {e.options}. Пожалуйста, уточните запрос.")

    except wikipedia.exceptions.PageError:
        search_url = f"https://google.com/search?q={search_query}"
        webbrowser.open(search_url)
        speaker_silero.say("Я не нашел информации по вашему запросу. Открыл Google для поиска.")

    except Exception as e:
        speaker_silero.say(f"Произошла ошибка при поиске: {str(e)}")

