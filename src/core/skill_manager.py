import importlib
import os
from pathlib import Path
from functools import lru_cache
import inspect


class SkillManager:
    """
    Загрузка, перезагрузка и выполнение навыков из директории src/skills.
    """
    def __init__(self, skills_path: str = "src/skills", debug: bool = False):
        self.skills_path = Path(skills_path)
        self.debug = debug
        self.skills = {}
        self.load_all_skills()

    def log(self, message: str):
        if self.debug:
            print(f"[DEBUG SkillManager] {message}")

    def load_all_skills(self):
        """Загружает все навыки из директории."""
        self.skills.clear()
        if not self.skills_path.exists():
            self.log(f"Директория навыков не найдена: {self.skills_path}")
            return
        for file in os.listdir(self.skills_path):
            if file.endswith(".py") and file != "__init__.py":
                name = file[:-3]
                module_name = f"src.skills.{name}"
                try:
                    module = importlib.import_module(module_name)
                    importlib.reload(module)
                    self.skills[name] = module
                    self.log(f"Загружен навык: {name}")
                except Exception as e:
                    print(f"[ERROR] Не удалось загрузить навык {name}: {e}")

    def reload(self):
        """Перезагружает все навыки (при изменении кода)."""
        self.load_all_skills()
        self.log("Все навыки перезагружены")

    def execute(self, action: str, text: str = None):
        """
        Выполняет действие.
        Формат action:
          - "module.function"
          - или просто "function" (ищем среди всех модулей).
        """
        if not action:
            return "⚠️ Действие не указано."

        def _call_function(fn):
            try:
                params = inspect.signature(fn).parameters
                if len(params) == 0:
                    return fn()
                elif "query" in params:
                    return fn(query=text)
                elif "text" in params:
                    return fn(text)
                else:
                    return fn()
            except Exception as e:
                return f"⚠️ Ошибка при выполнении '{action}': {e}"
            
        # Если указано модуль.функция
        if "." in action:
            mod, func = action.split(".", 1)
            module = self.skills.get(mod)

            if not module:
                return f"❌ Навык '{mod}' не найден."
            
            fn = getattr(module, func, None)
            if not callable(fn):
                return f"⚠️ В '{mod}' нет функции '{func}'."
            return _call_function(fn)

        # Ищем функцию по всем навыкам
        for name, module in self.skills.items():
            fn = getattr(module, action, None)
            if callable(fn):
                return _call_function(fn)
            
        return f"❌ Действие '{action}' не найдено."

    @lru_cache(maxsize=32)
    def list_skills(self):
        """Список доступных навыков (для справки)."""
        return list(self.skills.keys())
