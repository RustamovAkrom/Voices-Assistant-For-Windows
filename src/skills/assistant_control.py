import yaml
import sys
from pathlib import Path

def change_language(*args, **kwargs):
    """
    🌐 Меняет язык Jarvis через *args и **kwargs.

    В kwargs могут быть:
      - query: исходная голосовая команда
      - dataset: словарь команд (из commands.yaml)
      - context: системные данные (config, пути, язык, ассистент)
    """

    dataset = kwargs.get("dataset", {})
    query = kwargs.get("query", "")
    context = kwargs.get("context", {})

    # 🎯 Ищем язык в аргументах или из текста команды
    lang_code = None
    if args:
        for arg in args:
            if isinstance(arg, str):
                lang_code = arg
                break

    if not lang_code:
        # Если язык не передан напрямую — пробуем определить по query
        text = query.lower()
        if "англий" in text or "english" in text:
            lang_code = "en-US"
        elif "русск" in text or "russian" in text:
            lang_code = "ru-RU"
        elif "узбек" in text or "uzbek" in text:
            lang_code = "uz-UZ"

    if not lang_code:
        return "⚠️ Не понял, на какой язык переключиться."

    # 📂 Берём путь к конфигу из контекста или дефолтный
    config_path = Path(context.get("config_path", "data/config.yaml"))

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

        config["assistant"]["default_language"] = lang_code

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, allow_unicode=True)

        print(f"✅ Язык успешно изменён на {lang_code}")
        return f"✅ Язык успешно изменён на {lang_code}"

    except Exception as e:
        print(f"[ERROR] Ошибка изменения языка: {e}")
        return f"❌ Ошибка при изменении языка: {e}"


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
