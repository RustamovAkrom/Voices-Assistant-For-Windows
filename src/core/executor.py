from src.core.matcher import SmartMatcher

class Executor:
    def __init__(self, dataset, skill_manager):
        self.matcher = SmartMatcher(dataset)
        self.skills = skill_manager

    def handle(self, text: str) -> str:
        matches = self.matcher.find_matches(text)
        if not matches:
            return "Извини, я не понял, что ты сказал."

        responses = []
        for match in matches:
            skill = match["skill"]
            action = match["action"]
            result = self.skills.execute(skill, action)
            if result:
                responses.append(result)
            else:
                responses.append(match["response"])

        return " ".join(responses)
