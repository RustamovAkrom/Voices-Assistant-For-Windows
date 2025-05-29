import os
from core import settings

def close_app(app_name: str) -> str:
    """
    Закрывает указанное приложение, если оно запущено.
    
    :param app_name: Название приложения (например: 'chrome', 'notepad').
    :return: Статус выполнения команды.
    """
    app_name = app_name.lower().strip()
    apps: dict = settings.APPS_DIR  # Пример: {"chrome": "chrome.exe", "notepad": "notepad.exe"}

    matched_app = None
    for key in apps:
        if app_name in key:
            matched_app = apps[key]  # получаем exe-шник
            app_name = key  # для ответа
            break

    if not matched_app:
        return f"Приложение '{app_name}' не найдено в списке."

    try:
        result = os.system(f'taskkill /f /im "{matched_app}" >nul 2>&1')
        if result == 0:
            return f"✅ Приложение '{app_name}' успешно закрыто."
        else:
            return f"⚠ Не удалось закрыть '{app_name}' — возможно, оно не запущено."
    except Exception as e:
        return f"❌ Ошибка при закрытии '{app_name}': {str(e)}"
