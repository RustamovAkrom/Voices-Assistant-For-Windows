import importlib
import os
from pathlib import Path
from functools import lru_cache

class SkillManager:
    def __init__(self, skills_path: str = "src/skills", debug: bool = False):
        self.skills_path = Path(skills_path)
        self.debug = debug
        self.skills = {}
        self.load_all_skills()

    def load_all_skills(self):
        # clear and reload
        self.skills.clear()
        if not self.skills_path.exists():
            if self.debug:
                print(f"[DEBUG skills] skills path not found: {self.skills_path}")
            return
        for file in os.listdir(self.skills_path):
            if file.endswith(".py") and file != "__init__.py":
                name = file[:-3]
                module_name = f"src.skills.{name}"
                try:
                    module = importlib.import_module(module_name)
                    importlib.reload(module)
                    self.skills[name] = module
                    if self.debug:
                        print(f"[DEBUG skills] loaded: {name}")
                except Exception as e:
                    print(f"[ERROR skills] cannot load {module_name}: {e}")

    def reload(self):
        self.load_all_skills()

    def execute(self, action: str):
        """
        action: string name of function, we expect it's defined in some skill module.
        Strategy: try to find function in any loaded skill module.
        If action is like 'module.function' we can support that too.
        """
        # support format: "module.function"
        if "." in action:
            mod, func = action.split(".", 1)
            module = self.skills.get(mod)
            if not module:
                return f"❌ Навык '{mod}' не найден."
            fn = getattr(module, func, None)
            if not fn:
                return f"⚠️ Действие '{func}' отсутствует в '{mod}'."
            try:
                return fn()
            except Exception as e:
                return f"⚠️ Ошибка выполнения: {e}"

        # otherwise search function name in all modules
        for name, module in self.skills.items():
            fn = getattr(module, action, None)
            if callable(fn):
                try:
                    return fn()
                except Exception as e:
                    return f"⚠️ Ошибка выполнения: {e}"
        return f"❌ Действие '{action}' не найдено в зарегистрированных навыках."
