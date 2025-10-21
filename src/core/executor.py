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
        self.dataset = new_dataset
        self.matcher = SmartMatcher(self.dataset, threshold=self.matcher.threshold, debug=self.matcher.debug)

    def handle(self, text: str, lang: str = "en") -> str:
        """
        Обработка входного текста (строка). Возвращает ответ для TTS/печати.
        """
        matches = self.matcher.find_matches(text)
        if not matches:
            return "Извини, я не понял, что ты сказал."

        responses = []
        for m in matches:
            # meta commands (reload dataset/skills)
            if m["category"] == "meta":
                key = m["action"]  # e.g. 'reload_dataset' as defined in commands.yaml meta
                # meta handling is done outside (main) — but we can return response
                resp = m.get("response")
                if isinstance(resp, dict):
                    responses.append(resp.get(lang, resp.get("en", "Ok.")))
                else:
                    responses.append(str(resp))
                continue

            action = m.get("action")
            resp_cfg = m.get("response")
            # execute skill
            result = self.skill_manager.execute(action)
            # response selection: prefer skill return if non-empty, else dataset response (lang)
            if result and not result.startswith("❌") and not result.startswith("⚠️"):
                # skill returned human text — we use it, but still allow dataset phrasing
                responses.append(str(result))
            else:
                # fallback to dataset response for language
                if isinstance(resp_cfg, dict):
                    responses.append(resp_cfg.get(lang, resp_cfg.get("en", "")))
                else:
                    responses.append(str(resp_cfg or ""))
        # join responses with space
        return " ".join([r for r in responses if r])