from rapidfuzz import process, fuzz
from functools import lru_cache


class SmartMatcher:
    """
    SmartMatcher — модуль для интеллектуального сопоставления голосовых команд
    с заранее обученным датасетом (skills.yaml / settings.yaml).
    """

    def __init__(self, dataset: dict, threshold: int = 60, debug: bool = False):
        self.dataset = dataset or {}
        self.threshold = threshold
        self.debug = debug
        self.patterns = self._build_patterns()

    def log(self, *args):
        """Упрощённый логгер."""
        if self.debug:
            print("[DEBUG matcher]", *args)

    def _build_patterns(self):
        """
        Генерирует плоский список всех доступных шаблонов из dataset.
        Каждый элемент — кортеж:
        (pattern_lower, category, action, response_dict)
        """
        patterns = []
        skills = self.dataset.get("skills", {}) or {}

        for category, data in skills.items():
            commands = data.get("commands", []) or []
            for cmd in commands:
                pats = cmd.get("patterns", [])
                if isinstance(pats, dict):
                    # { "ru": [...], "en": [...] }
                    for lang, variants in pats.items():
                        for p in variants:
                            patterns.append(
                                (p.lower(), category, cmd.get("action"), cmd.get("response"))
                            )
                else:
                    for p in pats:
                        patterns.append(
                            (p.lower(), category, cmd.get("action"), cmd.get("response"))
                        )

        # Добавляем "meta" команды (системные, типа "перезагрузи", "останови", "помощь")
        meta = self.dataset.get("meta", {}) or {}
        for key, m in meta.items():
            for p in m.get("patterns", []):
                patterns.append((p.lower(), "meta", key, m.get("response")))

        self.log(f"patterns built: {len(patterns)}")
        return patterns

    @lru_cache(maxsize=2048)
    def _best_for_phrase(self, phrase: str):
        """
        Находит лучшее совпадение для конкретной фразы.
        Возвращает dict с {pattern, category, action, response, score}
        """
        if not phrase:
            return None

        choices = [p[0] for p in self.patterns]
        best = process.extractOne(
            phrase.lower(),
            choices,
            scorer=fuzz.token_set_ratio  # лучший для коротких фраз
        )

        if not best:
            return None

        matched_text, score, index = best
        if score < self.threshold:
            self.log(f"low match score={score} for '{phrase}'")
            return None

        patt, category, action, response = self.patterns[index]
        self.log(f"'{phrase}' → '{patt}' ({score}%) → action={action}")
        return {"pattern": patt, "category": category, "action": action, "response": response, "score": score}

    def split_phrases(self, text: str):
        """
        Разбивает длинную фразу на несколько подкоманд.
        Пример: "включи свет и открой окно" → ["включи свет", "открой окно"]
        """
        separators = [" и ", ",", ";", " а потом ", " затем ", " потом ", " then ", " and "]
        t = text
        for sep in separators:
            t = t.replace(sep, "|")
        parts = [p.strip() for p in t.split("|") if p.strip()]
        self.log("split →", parts)
        return parts

    def find_matches(self, text: str):
        """
        Находит все совпадения для текста пользователя.
        Возвращает список:
        [
            {"pattern": ..., "category": ..., "action": ..., "response": ..., "score": ...},
            ...
        ]
        """
        results = []
        for part in self.split_phrases(text):
            match = self._best_for_phrase(part)
            if match:
                results.append(match)
            else:
                self.log(f"no match for part: '{part}'")
        return results
