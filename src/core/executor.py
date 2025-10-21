from src.skills.gemeni_skill import GeminiSkill
from .matcher import SmartMatcher


class Executor:
    def __init__(self, dataset: dict, skill_manager, config: dict = None):
        self.config = config or {}
        self.dataset = dataset or {}
        self.skill_manager = skill_manager
        threshold = self.config.get("matcher_threshold", 60)
        debug = self.config.get("debug", False)
        self.matcher = SmartMatcher(self.dataset, threshold=threshold, debug=debug)

    def update_dataset(self, new_dataset: dict):
        self.dataset = new_dataset or {}
        self.matcher = SmartMatcher(self.dataset, threshold=self.matcher.threshold, debug=self.matcher.debug)

    def handle(self, text: str, lang: str = "en") -> str:
        """
        Обрабатывает входной текст и возвращает ответ для TTS/печати.
        """
        matches = self.matcher.find_matches(text)
        if not matches:
            gemini_conf = self.config.get("assistant", {})
            if gemini_conf.get("gemeni_enabled", False):
                ai = GeminiSkill(
                    api_key=gemini_conf.get("gemini_api_key"),
                    enabled=True,
                    debug=self.config.get("debug", False)
                )
                return ai.ask(text, lang)
            else:
                return {
                    "ru": "Извини, я не понял, что ты сказал.",
                    "en": "Sorry, I did not understand.",
                    "uz": "Kechirasiz, men tushunmadim."
                }.get(lang, "Извини, я не понял.")
        
        responses = []
        for m in matches:
            if m["category"] == "meta":
                # Мета-команда (reload/restart)
                key = m["action"]  # например 'reload_dataset'
                resp = m.get("response", "")
                if isinstance(resp, dict):
                    responses.append(resp.get(lang, resp.get("en", "")))
                else:
                    responses.append(str(resp))
                continue

            action = m.get("action")
            resp_cfg = m.get("response")
            # выполнение скилла
            result = self.skill_manager.execute(action)
            if result and not (str(result).startswith("❌") or str(result).startswith("⚠️")):
                # если скилл вернул текст — используем его
                responses.append(str(result))
            else:
                # иначе отдаём ответ из датасета по языку
                if isinstance(resp_cfg, dict):
                    responses.append(resp_cfg.get(lang, resp_cfg.get("en", "")))
                else:
                    responses.append(str(resp_cfg or ""))
        return " ".join([r for r in responses if r])
