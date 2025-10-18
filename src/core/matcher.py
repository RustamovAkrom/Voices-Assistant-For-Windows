from rapidfuzz import process, fuzz
from functools import lru_cache

class SmartMatcher:
    def __init__(self, dataset: dict, threshold: int = 60, debug: bool = False):
        self.dataset = dataset or {}
        self.threshold = threshold
        self.debug = debug
        # patterns: list of tuples (pattern_lower, category, action, response_dict)
        self.patterns = self._build_patterns()

    def _build_patterns(self):
        patterns = []
        skills = self.dataset.get("skills", {}) or {}
        for category, data in skills.items():
            for cmd in data.get("commands", []):
                # support patterns as list OR patterns_lang dict
                pats = cmd.get("patterns", [])
                if isinstance(pats, dict):
                    # dict like {ru:[], en:[]}
                    for lang, lst in pats.items():
                        for p in lst:
                            patterns.append((p.lower(), category, cmd.get("action"), cmd.get("response")))
                else:
                    for p in pats:
                        patterns.append((p.lower(), category, cmd.get("action"), cmd.get("response")))
        # meta commands
        meta = self.dataset.get("meta", {}) or {}
        for key, m in meta.items():
            for p in m.get("patterns", []):
                patterns.append((p.lower(), "meta", key, m.get("response")))
        return patterns

    @lru_cache(maxsize=2048)
    def _best_for_phrase(self, phrase: str):
        if not phrase:
            return None
        choices = [p[0] for p in self.patterns]
        # use token_set_ratio which is robust for short phrases
        best = process.extractOne(phrase.lower(), choices, scorer=fuzz.token_set_ratio)
        if not best:
            return None
        matched_text, score, index = best
        if self.debug:
            print(f"[DEBUG matcher] phrase='{phrase}' best='{matched_text}' score={score}")
        if score >= self.threshold:
            patt, category, action, response = self.patterns[index]
            return {"pattern": patt, "category": category, "action": action, "response": response, "score": score}
        return None

    def split_phrases(self, text: str):
        # разделители — можно расширять
        separators = [" и ", ",", ";", " а потом ", " затем ", " потом ", " then ", " and "]
        t = text
        for sep in separators:
            t = t.replace(sep, "|")
        parts = [p.strip() for p in t.split("|") if p.strip()]
        if self.debug:
            print(f"[DEBUG matcher] split -> {parts}")
        return parts

    def find_matches(self, text: str):
        """
        Возвращает список совпадений в формате:
        {pattern, category, action, response, score}
        """
        results = []
        parts = self.split_phrases(text)
        for part in parts:
            match = self._best_for_phrase(part)
            if match:
                results.append(match)
            elif self.debug:
                print(f"[DEBUG matcher] no match for part: '{part}'")
        return results
