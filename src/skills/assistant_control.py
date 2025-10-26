import re
from pathlib import Path
import yaml
import sys

from src.core.config import get_settings, DEFAULT_CONFIG_PATH

def _detect_lang_from_text(text: str):
    if not text:
        return None
    t = text.lower()
    mapping = {
        "русский": "ru", "русски": "ru", "russian": "ru", "ru": "ru", "ru-ru": "ru",
        "английский": "en", "англиский": "en", "english": "en", "en": "en", "en-us": "en",
        "узбекский": "uz", "uzbek": "uz", "uz": "uz"
    }
    for token in re.split(r"[\s,\.]+", t):
        if token in mapping:
            return mapping[token]
    m = re.search(r"\b([a-z]{2})(?:[-_][A-Z]{2})?\b", t)
    if m:
        code = m.group(1).lower()
        return mapping.get(code, code)
    return None

def _persist_settings(settings):
    """
    Если get_settings() вернул dict и у нас есть DEFAULT_CONFIG_PATH — сохраняем.
    Безопасно игнорируем ошибки.
    """
    try:
        if isinstance(settings, dict) and DEFAULT_CONFIG_PATH:
            DEFAULT_CONFIG_PATH.write_text(yaml.safe_dump(settings, allow_unicode=True))
    except Exception:
        pass

def change_language(*args, **kwargs):
    """
    Skills handler for 'change language' command.
    Uses central settings (get_settings()) instead of manual file access.
    Expects kwargs.get('text') with user phrase.
    Optionally in kwargs: recognizer, tts — will be updated if present.
    Returns localized confirmation string.
    """
    text = kwargs.get("text", "") or " ".join(str(a) for a in args if isinstance(a, str))
    lang = _detect_lang_from_text(text)
    if not lang:
        return {
            "ru": "Какой язык установить? (русский, английский, узбекский)",
            "en": "Which language to set? (russian, english, uzbek)",
            "uz": "Qaysi tilni o'rnatish kerak? (ruscha, inglizcha, o'zbekcha)"
        }.get(kwargs.get("lang", "ru"), "Какой язык установить?")

    # Получаем централизованные настройки
    settings = None
    try:
        settings = get_settings() or {}
    except Exception:
        settings = {}

    # Обновляем runtime-объекты, если переданы
    recognizer = kwargs.get("recognizer")
    tts = kwargs.get("tts")

    try:
        if recognizer and hasattr(recognizer, "set_language"):
            recognizer.set_language(lang)
        if tts and hasattr(tts, "set_language"):
            tts.set_language(lang)
    except Exception:
        pass

    # Обновляем settings в памяти и сохраняем, если возможно
    try:
        if isinstance(settings, dict):
            settings.setdefault("assistant", {})["default_language"] = lang
            _persist_settings(settings)
        else:
            # если get_settings() вернул объект (dataclass/Settings) — пробуем установить поле
            try:
                setattr(settings, "assistant", getattr(settings, "assistant", {}))
                if isinstance(settings.assistant, dict):
                    settings.assistant["default_language"] = lang
                _persist_settings(getattr(settings, "__dict__", None) or settings)
            except Exception:
                pass
    except Exception:
        pass

    messages = {
        "ru": "Язык обновлён.",
        "en": "Language updated.",
        "uz": "Til yangilandi."
    }
    return messages.get(lang, messages["ru"])
# ...existing code...

def shutdown_assistant(*args, **kwargs):
    """
    🛑 Корректно завершает работу Jarvis.

    В kwargs можно передавать:
      - context: { "workers": [...], "assistant_name": str }
      - query: исходная команда пользователя
    """

    context = kwargs.get("context", {})
    query = kwargs.get("query", "")
    assistant_name = context.get("assistant_name", "Jarvis")
    workers = context.get("workers", [])

    print(f"🧠 {assistant_name} получил команду завершения: {query}")
    print("🔻 Завершение активных процессов...")

    for w in workers:
        if hasattr(w, "stop"):
            try:
                w.stop()
                print(f"✅ Остановлен поток: {getattr(w, 'name', 'Unnamed')}")
            except Exception as e:
                print(f"⚠️ Не удалось остановить поток: {e}")

    print(f"👋 {assistant_name} завершает работу.")
    sys.exit(0)
