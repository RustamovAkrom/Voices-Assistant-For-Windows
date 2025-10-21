import os
import requests
from typing import Optional

class GeminiSkill:
    """
    Навык общения с AI (Google Gemini)
    Безопасная, оптимизированная версия с автоматической проверкой ключа и сети.
    """

    def __init__(self, api_key: Optional[str] = None, enabled: bool = True, debug: bool = False):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.enabled = enabled and bool(self.api_key)
        self.debug = debug
        self.endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

    def ask(self, prompt: str, lang: str = "ru") -> str:
        """
        Отправляет текст в Gemini и возвращает ответ.
        Если API выключен, отсутствует ключ или нет сети — выдаёт корректное сообщение.
        """
        if not self.enabled:
            if self.debug:
                print("[GeminiSkill] AI модуль отключён или не настроен.")
            return "🤖 AI-модуль сейчас не активен."

        if not self.api_key:
            if self.debug:
                print("[GeminiSkill] API ключ Gemini отсутствует.")
            return "⚠️ Не найден ключ Gemini API. Добавьте его в настройки."

        headers = {"Content-Type": "application/json"}
        params = {"key": self.api_key}
        data = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }

        try:
            response = requests.post(
                self.endpoint,
                headers=headers,
                params=params,
                json=data,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                text = (
                    result.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "")
                    .strip()
                )
                if not text:
                    text = "🤖 Извини, я не смог придумать ответ."
                if self.debug:
                    print(f"[GeminiSkill] ✅ Response: {text}")
                return text

            # Обработка API-ошибок
            if self.debug:
                print(f"[GeminiSkill] ❌ API Error {response.status_code}: {response.text}")
            return "⚠️ Ошибка при обращении к AI. Попробуйте позже."

        except requests.exceptions.Timeout:
            if self.debug:
                print("[GeminiSkill] ⏳ Превышено время ожидания ответа от API.")
            return "⚠️ AI не ответил вовремя."
        except requests.exceptions.ConnectionError:
            if self.debug:
                print("[GeminiSkill] 🌐 Нет подключения к сети.")
            return "⚠️ Нет подключения к сети. Работаю офлайн."
        except Exception as e:
            if self.debug:
                print(f"[GeminiSkill] ❗ Ошибка: {e}")
            return "⚠️ Произошла непредвиденная ошибка при обращении к AI."
