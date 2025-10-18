from rapidfuzz import fuzz, process

class SmartMatcher:
    def __init__(self, dataset):
        self.dataset = dataset
        self.patterns = self._extract_patterns()

    def _extract_patterns(self):
        patterns = []
        for skill, data in self.dataset["skills"].items():
            for cmd in data["commands"]:
                for p in cmd["patterns"]:
                    patterns.append((p, skill, cmd["action"], cmd["response"]))
        return patterns

    def split_phrases(self, text):
        for sep in [" и ", ",", " а потом ", " затем "]:
            text = text.replace(sep, "|")
        return [t.strip() for t in text.split("|") if t.strip()]

    def find_matches(self, text):
        phrases = self.split_phrases(text)
        matches = []

        for phrase in phrases:
            choices = [p[0] for p in self.patterns]
            best_match, score, index = process.extractOne(phrase, choices, scorer=fuzz.token_sort_ratio)
            if score >= 60:
                pattern, skill, action, response = self.patterns[index]
                matches.append({"skill": skill, "action": action, "response": response})
        return matches
