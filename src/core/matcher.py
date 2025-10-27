# ...existing code...
from rapidfuzz import process, fuzz
from functools import lru_cache
import re

class SmartMatcher:
    """
    Улучшенный сопоставитель команд.
    Теперь поддерживает 3 категории верхнего уровня:
    - skills
    - meta
    - smalltalk
    """

    def __init__(self, dataset: dict, threshold: int = 70, debug: bool = False, config: dict = None):
        self.dataset = dataset or {}
        self.threshold = threshold
        self.debug = debug
        self.config = config or {}
        # Собираем wake-words из конфигурации (если есть)
        self.wake_words = set()
        try:
            ww = self.config.get("wake_words", {}) or {}
            if isinstance(ww, dict):
                for v in ww.values():
                    if isinstance(v, (list, tuple)):
                        self.wake_words.update([w.lower() for w in v])
                    elif isinstance(v, str):
                        self.wake_words.add(v.lower())
            elif isinstance(ww, (list, tuple)):
                self.wake_words.update([w.lower() for w in ww])
            single = self.config.get("wake_word")
            if single:
                self.wake_words.add(single.lower())
        except Exception:
            pass

        # паттерны будут содержать: (orig, normalized, category, key, action, response)
        self.patterns = self._build_patterns()

    def log(self, *args):
        if self.debug:
            print("[DEBUG matcher]", *args)

    def _build_patterns(self):
        patterns = []

        # === Skills ===
        skills = self.dataset.get("skills", {}) or {}
        for category, data in skills.items():
            for idx, cmd in enumerate(data.get("commands", [])):
                pats = cmd.get("patterns", [])
                if isinstance(pats, str):
                    pats = [pats]
                for p in pats:
                    norm = self._normalize(p)
                    patterns.append((p, norm, "skills", category, cmd.get("action"), cmd.get("response", "")))

        # === Meta ===
        meta = self.dataset.get("meta", {}) or {}
        for key, m in meta.items():
            for p in m.get("patterns", []):
                norm = self._normalize(p)
                patterns.append((p, norm, "meta", key, None, m.get("response", "")))

        # === Smalltalk ===
        smalltalk = self.dataset.get("smalltalk", {}) or {}
        commands = smalltalk.get("commands", [])
        for idx, cmd in enumerate(commands):
            pats = cmd.get("patterns", [])
            if isinstance(pats, dict):
                all_pats = []
                for v in pats.values():
                    if isinstance(v, list):
                        all_pats.extend(v)
                    else:
                        all_pats.append(v)
            else:
                all_pats = pats or []
            for p in all_pats:
                norm = self._normalize(p)
                patterns.append((p, norm, "smalltalk", f"smalltalk_{idx}", None, cmd.get("response", "")))

        self.log(f"Loaded {len(patterns)} patterns total.")
        return patterns

    def _normalize(self, text: str) -> str:
        if not text:
            return ""

        # нормализация базовая
        text = re.sub(r"[^\w\s']", " ", str(text), flags=re.UNICODE).lower()

        # удаляем wake-words в разных позициях
        if self.wake_words:
            for w in sorted(self.wake_words, key=len, reverse=True):
                # удаляем как отдельное слово
                text = re.sub(rf"\b{re.escape(w)}\b", " ", text)

        # расширенные стоп-слова на трёх языках
        stopwords = {
            "ru": ["пожалуйста", "пжлст", "скажи", "скажи мне", "потом", "и", "ещё", "еще", "пожалуйстa", "но", "так", "вообще", "иногда", "хорошо", "давай", "да"],
            "en": ["please", "and", "then", "say", "tell", "now", "hey", "ok", "please"],
            "uz": ["iltimos", "keyin", "va", "ayt", "и", "yana"]
        }
        sw = set()
        for v in stopwords.values():
            sw.update(v)

        tokens = [t for t in text.split() if t and t not in sw]
        return " ".join(tokens).strip()

    @lru_cache(maxsize=2048)
    def _best_for_phrase(self, phrase: str):
        if not phrase:
            return None

        normalized = self._normalize(phrase)
        if not normalized:
            return None

        # choices — нормализованные паттерны
        choices = [p[1] for p in self.patterns]
        if not choices:
            return None

        # 1) основной проход — token_set_ratio
        best_a = process.extractOne(normalized, choices, scorer=fuzz.token_set_ratio)
        # 2) частичный проход — partial_ratio (лучше для длинных/фрагментированных фраз)
        best_b = process.extractOne(normalized, choices, scorer=fuzz.partial_ratio)

        candidates = [b for b in (best_a, best_b) if b]
        if not candidates:
            return None

        best = max(candidates, key=lambda x: x[1])  # (match, score, idx)
        score = best[1]
        idx = best[2]
        pattern_entry = self.patterns[idx]
        category = pattern_entry[2]

        # если хороший score >= порога — принимаем
        if score >= self.threshold:
            return {
                "pattern": pattern_entry[0],
                "category": category,
                "key": pattern_entry[3],
                "action": pattern_entry[4],
                "response": pattern_entry[5],
                "score": score,
            }

        # fallback 1: для smalltalk допускаем низкий порог (короткие/эмоциональные фразы)
        if category == "smalltalk" and score >= max(30, self.threshold - 30):
            return {
                "pattern": pattern_entry[0],
                "category": category,
                "key": pattern_entry[3],
                "action": pattern_entry[4],
                "response": pattern_entry[5],
                "score": score,
            }

        # fallback 2: пытаемся ещё раз с более мягким порогом и partial scorer
        fallback_threshold = max(45, int(self.threshold * 0.7))
        if best_b and best_b[1] >= fallback_threshold:
            fb_idx = best_b[2]
            fb_entry = self.patterns[fb_idx]
            return {
                "pattern": fb_entry[0],
                "category": fb_entry[2],
                "key": fb_entry[3],
                "action": fb_entry[4],
                "response": fb_entry[5],
                "score": best_b[1],
            }

        # нет подходящего кандидата
        self.log(f"No good match for '{phrase}' (best={score})")
        return None

    def split_phrases(self, text: str):
        if not text:
            return []
        t = text.lower()
        # common separators in RU/EN/UZ to split multiple commands
        for sep in [" и ", " а потом ", " затем ", " потом ", " потом же ", " затем же ", " then ", " and ", " keyin ", "yana", "va"]:
            t = t.replace(sep, " | ")
        return [p.strip() for p in t.split("|") if p.strip()]

    def find_matches(self, text: str):
        matches = []
        if not text:
            return matches
        for part in self.split_phrases(text):
            best = self._best_for_phrase(part)
            if best:
                matches.append(best)
        return matches
# ...existing code...

# # filepath: [matcher.py](http://_vscodecontentref_/1)
# # ...existing code...
# from rapidfuzz import process, fuzz
# from functools import lru_cache
# import re

# class SmartMatcher:
#     """
#     Улучшенный сопоставитель команд.
#     Теперь поддерживает 3 категории верхнего уровня:
#     - skills
#     - meta
#     - smalltalk
#     """

#     def __init__(self, dataset: dict, threshold: int = 60, debug: bool = False):
#         self.dataset = dataset or {}
#         self.threshold = threshold
#         self.debug = debug
#         self.patterns = self._build_patterns()

#     def log(self, *args):
#         if self.debug:
#             print("[DEBUG matcher]", *args)

#     def _build_patterns(self):
#         patterns = []

#         # === Skills ===
#         skills = self.dataset.get("skills", {}) or {}
#         for category, data in skills.items():
#             for idx, cmd in enumerate(data.get("commands", [])):
#                 pats = cmd.get("patterns", [])
#                 if isinstance(pats, str):
#                     pats = [pats]
#                 for p in pats:
#                     patterns.append((p, "skills", category, cmd.get("action"), cmd.get("response", "")))

#         # === Meta ===
#         meta = self.dataset.get("meta", {}) or {}
#         for key, m in meta.items():
#             for p in m.get("patterns", []):
#                 patterns.append((p, "meta", key, None, m.get("response", "")))

#         # === Smalltalk ===
#         smalltalk = self.dataset.get("smalltalk", {}) or {}
#         commands = smalltalk.get("commands", [])
#         for idx, cmd in enumerate(commands):
#             pats = cmd.get("patterns", [])
#             if isinstance(pats, dict):
#                 all_pats = []
#                 for v in pats.values():
#                     if isinstance(v, list):
#                         all_pats.extend(v)
#                     else:
#                         all_pats.append(v)
#             else:
#                 all_pats = pats or []
#             for p in all_pats:
#                 patterns.append((p, "smalltalk", f"smalltalk_{idx}", None, cmd.get("response", "")))

#         self.log(f"Loaded {len(patterns)} patterns total.")
#         return patterns

#     def _normalize(self, text: str) -> str:
#         if not text:
#             return ""
        
#         # простая очистка пунктуации
#         text = re.sub(r"[^\w\s']", " ", text, flags=re.UNICODE).lower()

#         # простые стоп-слова (можно расширять/локализовать)
#         stopwords = {
#             "ru": ["пожалуйста", "пжлст", "скажи", "скажи мне", "потом", "и", "ещё", "еще", "пожалуйста", "пожалуйстa"],
#             "en": ["please", "and", "then", "say", "tell", "now"],
#             "uz": ["iltimos", "keyin", "va", "ayt"]
#         }

#         sw = set(sum(stopwords.values(), []))
#         tokens = [t for t in text.split() if t and t not in sw]
#         return " ".join(tokens)
    
#     @lru_cache(maxsize=2048)
#     def _best_for_phrase(self, phrase: str):
#         if not phrase:
#             return None
        
#         normalized = self._normalize(phrase)
#         if not normalized:
#             return None

#         choices = [p[0] for p in self.patterns]
#         if not choices:
#             return None

#         best_a = process.extractOne(normalized, choices, scorer=fuzz.token_set_ratio)
#         best_b = process.extractOne(normalized, choices, scorer=fuzz.token_sort_ratio)

#         candidates = [b for b in (best_a, best_b) if b]
#         if not candidates:
#             return None

#         # b = (match, score, idx)
#         best = max(candidates, key=lambda x: x[1])
#         if best[1] < self.threshold:
#             self.log(f"No good match for '{phrase}' (best={best[1]})")
#             return None

#         patt = best[0]
#         score = best[1]
#         idx = best[2]
#         pattern_entry = self.patterns[idx]
#         return {
#             "pattern": patt,
#             "category": pattern_entry[1],
#             "key": pattern_entry[2],
#             "action": pattern_entry[3],
#             "response": pattern_entry[4],
#             "score": score,
#         }

#     def split_phrases(self, text: str):
#         for sep in [" и ", " а потом ", " затем ", " потом ", " then ", " and ", "keyin", "yana", "undan keyin"]:
#             text = text.replace(sep, " | ")
#         return [p.strip() for p in text.split("|") if p.strip()]

#     def find_matches(self, text: str):
#         matches = []
#         if not text:
#             return matches
#         for part in self.split_phrases(text):
#             best = self._best_for_phrase(part)
#             if best:
#                 matches.append(best)
#         return matches