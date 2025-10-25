from rapidfuzz import process, fuzz
from functools import lru_cache

class SmartMatcher:
    """
    Улучшенный сопоставитель команд.
    Теперь поддерживает 3 категории верхнего уровня:
    - skills
    - meta
    - smalltalk
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

        # === Skills ===
        skills = self.dataset.get("skills", {}) or {}
        for category, data in skills.items():
            for cmd in data.get("commands", []):
                pats = cmd.get("patterns", [])
                if isinstance(pats, dict):
                    # Если в будущем будут языковые паттерны
                    all_pats = sum(pats.values(), [])
                else:
                    all_pats = pats
                for p in all_pats:
                    patterns.append((
                        p.lower(),
                        "skills",
                        category,
                        cmd.get("action"),
                        cmd.get("response")
                    ))

        # === Meta ===
        meta = self.dataset.get("meta", {}) or {}
        for key, m in meta.items():
            for p in m.get("patterns", []):
                patterns.append((
                    p.lower(),
                    "meta",
                    key,
                    None,
                    m.get("response")
                ))

        # === Smalltalk ===
        smalltalk = self.dataset.get("smalltalk", {}) or {}
        commands = smalltalk.get("commands", [])
        for cmd in commands:
            pats = cmd.get("patterns", [])
            if isinstance(pats, dict):
                all_pats = sum(pats.values(), [])
            else:
                all_pats = pats
            for p in all_pats:
                patterns.append((
                    p.lower(),
                    "smalltalk",
                    None,
                    None,
                    cmd.get("response")
                ))

        self.log(f"Loaded {len(patterns)} patterns total.")
        return patterns

    @lru_cache(maxsize=2048)
    def _best_for_phrase(self, phrase: str):
        if not phrase:
            return None
        choices = [p[0] for p in self.patterns]
        best = process.extractOne(phrase.lower(), choices, scorer=fuzz.token_set_ratio)
        if not best or best[1] < self.threshold:
            return None

        patt, category, key, action, response = self.patterns[best[2]]
        return {
            "pattern": patt,
            "category": category,  # skills / meta / smalltalk
            "key": key,
            "action": action,
            "response": response,
            "score": best[1],
        }

    def split_phrases(self, text: str):
        for sep in [" и ", " а потом ", " затем ", " потом ", " then ", " and ", "keyin", "yana", "undan keyin"]:
            text = text.replace(sep, "|")
        return [p.strip() for p in text.split("|") if p.strip()]

    def find_matches(self, text: str):
        matches = []
        for part in self.split_phrases(text):
            best = self._best_for_phrase(part)
            if best:
                matches.append(best)
                self.log(f"Matched: {part} -> {best}")
        return matches

# from rapidfuzz import process, fuzz
# from functools import lru_cache

# class SmartMatcher:
#     def __init__(self, dataset: dict, threshold: int = 60, debug: bool = False):
#         self.dataset = dataset or {}
#         self.threshold = threshold
#         self.debug = debug
#         self.patterns = self._build_patterns()

#     def log(self, *args):
#         if self.debug:
#             print("[DEBUG matcher]", *args)

#     def _build_patterns(self):
#         skills = self.dataset.get("skills", {}) or {}
#         patterns = [
#             (p.lower(), category, cmd.get("action"), cmd.get("response"))
#             for category, data in skills.items()
#             for cmd in data.get("commands", [])
#             for pats in ([cmd["patterns"]] if not isinstance(cmd["patterns"], dict)
#                          else cmd["patterns"].values())
#             for p in (pats if isinstance(pats, list) else [pats])
#         ]
#         meta = self.dataset.get("meta", {}) or {}
#         for key, m in meta.items():
#             for p in m.get("patterns", []):
#                 patterns.append((p.lower(), "meta", key, m.get("response")))
#         return patterns

#     @lru_cache(maxsize=2048)
#     def _best_for_phrase(self, phrase: str):
#         if not phrase:
#             return None
#         choices = [p[0] for p in self.patterns]
#         best = process.extractOne(phrase.lower(), choices, scorer=fuzz.token_set_ratio)
#         if not best or best[1] < self.threshold:
#             return None
#         patt, category, action, response = self.patterns[best[2]]
#         return {"pattern": patt, "category": category, "action": action, "response": response, "score": best[1]}

#     def split_phrases(self, text: str):
#         for sep in [" и ", " а потом ", " затем ", " потом ", " then ", " and ", "keyin", "yana", "undan keyin"]:
#             text = text.replace(sep, "|")
#         return [p.strip() for p in text.split("|") if p.strip()]

#     def find_matches(self, text: str):
#         return [m for part in self.split_phrases(text) if (m := self._best_for_phrase(part))]
