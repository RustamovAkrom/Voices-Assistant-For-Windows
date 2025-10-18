import importlib
import os
from pathlib import Path

class SkillManager:
    def __init__(self):
        self.skills = {}
        self.load_all_skills()

    def load_all_skills(self):
        skills_dir = Path(__file__).parent.parent / "skills"
        for file in os.listdir(skills_dir):
            if file.endswith(".py") and file != "__init__.py":
                module_name = f"src.skills.{file[:-3]}"
                module = importlib.import_module(module_name)
                self.skills[file[:-3]] = module

    def execute(self, skill_name, action):
        skill = self.skills.get(skill_name)
        if not skill:
            return f"Навык '{skill_name}' не найден."

        func = getattr(skill, action, None)
        if not func:
            return f"Действие '{action}' отсутствует в '{skill_name}'."

        return func()
