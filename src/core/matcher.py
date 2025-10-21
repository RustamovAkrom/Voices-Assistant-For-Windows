from rapidfuzz import process, fuzz
from functools import lru_cache

class SmartMatcher:
    """
    Интеллектуальное сопоставление команд с шаблонами из dataset.
    """
    def __init__(self, dataset: dict, threshold: int = 60, debug: bool = False):
        self.dataset = dataset or {}
        self.threshold = threshold
        self.debug = debug
        self.patterns = self._build_patterns()

    def log(self, *args):
        if self.debug:
            print("[DEBUG matcher]", *args)

    def _build_patterns(self):
        patterns = []
        skills = self.dataset.get("skills", {}) or {}
        for category, data in skills.items():
            for cmd in data.get("commands", []):
                pats = cmd.get("patterns", [])
                # Поддерживаем словарь языков
                if isinstance(pats, dict):
                    for variants in pats.values():
                        for p in variants:
                            patterns.append((p.lower(), category, cmd.get("action"), cmd.get("response")))
                else:
                    for p in pats:
                        patterns.append((p.lower(), category, cmd.get("action"), cmd.get("response")))
        # Метакоманды из секции "meta"
        meta = self.dataset.get("meta", {}) or {}
        for key, m in meta.items():
            for p in m.get("patterns", []):
                patterns.append((p.lower(), "meta", key, m.get("response")))
        self.log(f"patterns built: {len(patterns)}")
        return patterns

    @lru_cache(maxsize=2048)
    def _best_for_phrase(self, phrase: str):
        if not phrase:
            return None
        choices = [p[0] for p in self.patterns]
        best = process.extractOne(
            phrase.lower(),
            choices,
            scorer=fuzz.token_set_ratio  # хорошо работает для коротких фраз
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
        # Разбиваем по разделителям для нескольких команд в одной фразе
        separators = [" и ", ",", ";", " а потом ", " затем ", " потом ", " then ", " and "]
        t = text
        for sep in separators:
            t = t.replace(sep, "|")
        parts = [p.strip() for p in t.split("|") if p.strip()]
        self.log("split →", parts)
        return parts

    def find_matches(self, text: str):
        results = []
        for part in self.split_phrases(text):
            match = self._best_for_phrase(part)
            if match:
                results.append(match)
            else:
                self.log(f"no match for part: '{part}'")
        return results
