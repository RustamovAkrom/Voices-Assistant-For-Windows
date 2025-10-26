from src.skills.gemeni_skill import GeminiSkill
from .matcher import SmartMatcher

class Executor:
    def __init__(self, dataset: dict, skill_manager, config: dict = None):
        self.config = config or {}
        self.dataset = dataset or {}
        self.skill_manager = skill_manager
        self._init_matcher()

    def _init_matcher(self):
        self.matcher = SmartMatcher(
            self.dataset,
            threshold=self.config.get("matcher_threshold", 60),
            debug=self.config.get("debug", False),
            config=self.config
        )

    def update_dataset(self, new_dataset: dict):
        self.dataset = new_dataset or {}
        self._init_matcher()

    def handle(self, text: str, lang: str = "ru") -> str:
        matches = self.matcher.find_matches(text)

        if not matches:
            # AI
            gem_conf = self.config.get("assistant", {})
            if gem_conf.get("gemeni_enabled") and gem_conf.get("gemini_api_key"):
                ai = GeminiSkill(
                    api_key=gem_conf["gemini_api_key"],
                    enabled=True,
                    debug=self.config.get("debug", False)
                )
                return ai.ask(text, lang)
            
            return {
                "ru": "Извини, я не понял, что ты сказал.",
                "en": "Sorry, I did not understand.",
                "uz": "Kechirasiz, men tushunmadim."
            }.get(lang, "Извини, я не понял.")

        responses = []
        for match in matches:
            category = match.get("category")
            action = match.get("action")
            resp_cfg = match.get("response", "")

            if category == "meta":
                if isinstance(resp_cfg, dict):
                    responses.append(resp_cfg.get(lang, resp_cfg.get("en", "")))
                else:
                    responses.append(str(resp_cfg))
                continue
            
            if category == "smalltalk":
                if isinstance(resp_cfg, dict):
                    responses.append(resp_cfg.get(lang, resp_cfg.get("en", "")))
                else:
                    responses.append(str(resp_cfg))
                continue

            result = self.skill_manager.execute(action, text)
            if result and not str(result).startswith(("❌", "⚠️")):
                responses.append(str(result))
            else:
                if isinstance(resp_cfg, dict):
                    responses.append(resp_cfg.get(lang, resp_cfg.get("en", "")))
                else:
                    responses.append(str(resp_cfg or ""))

        return " ".join(filter(None, responses))
