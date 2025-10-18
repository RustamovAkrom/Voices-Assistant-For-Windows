from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

class LanguageDetector:
    SUPPORTED = {"ru", "en", "uz"}

    def detect(self, text: str) -> str:
        if not text or not text.strip():
            return "en"
        try:
            code = detect(text)
            if code in self.SUPPORTED:
                return code
            # частые случаи: uz может быть определён как tr/tl — fallback to uz if Uzbek words present not handled here
            return "en"
        except LangDetectException:
            return "en"
