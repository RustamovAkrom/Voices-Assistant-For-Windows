from langdetect import detect, DetectorFactory
import re

DetectorFactory.seed = 0  # делает результаты стабильными

class LanguageDetector:
    SUPPORTED = ["ru", "en", "uz"]

    def __init__(self):
        pass

    def clean_text(self, text: str) -> str:
        """
        Убираем служебные слова и символы, чтобы не мешали детекции
        """
        text = text.lower()
        text = re.sub(r"[^a-zа-яёҳўқғӣ'\s]", "", text)
        text = text.strip()
        return text

    def detect_language(self, text: str) -> str:
        """
        Определяет язык текста (ru, en, uz)
        """
        if not text or len(text.strip()) < 2:
            return "ru"

        text = self.clean_text(text)

        try:
            lang = detect(text)
            if lang not in self.SUPPORTED:
                # fallback через эвристику (узбек часто не определяется)
                if re.search(r"[ўқғҳ]", text):  # типичные узбекские буквы
                    return "uz"
                elif re.search(r"[a-z]", text):
                    return "en"
                elif re.search(r"[а-яё]", text):
                    return "ru"
                return "ru"
            return lang
        
        except Exception:
            # fallback на символы
            if re.search(r"[ўқғҳ]", text):
                return "uz"
            elif re.search(r"[a-z]", text):
                return "en"
            elif re.search(r"[а-яё]", text):
                return "ru"
            return "ru"
