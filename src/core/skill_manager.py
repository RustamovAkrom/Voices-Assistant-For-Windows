import importlib
import os
from pathlib import Path
from functools import lru_cache

class SkillManager:
    """
    Класс SkillManager отвечает за загрузку, перезагрузку и выполнение "навыков" (skills)
    из директории src/skills. Каждый навык — это обычный .py файл с функциями.
    """

    def __init__(self, skills_path: str = "src/skills", debug: bool = False):
        self.skills_path = Path(skills_path)
        self.debug = debug
        self.skills = {}
        self.load_all_skills()

    def log(self, message: str):
        """Упрощённый логгер."""
        if self.debug:
            print(f"[DEBUG SkillManager] {message}")

    def load_all_skills(self):
        """Загружает все навыки из указанной директории."""
        self.skills.clear()

        if not self.skills_path.exists():
            self.log(f"Директория с навыками не найдена: {self.skills_path}")
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
                    print(f"[ERROR] Не удалось загрузить {module_name}: {e}")

    def reload(self):
        """Перезагружает все навыки (например, при изменении кода во время работы)."""
        self.load_all_skills()
        self.log("Все навыки перезагружены")

    def execute(self, action: str):
        """
        Выполняет указанное действие.
        Поддерживает два формата:
          1. "имя_функции"
          2. "модуль.функция"
        """
        if not action:
            return "⚠️ Не указано действие."

        # формат: "module.function"
        if "." in action:
            mod, func = action.split(".", 1)
            module = self.skills.get(mod)
            if not module:
                return f"❌ Навык '{mod}' не найден."
            fn = getattr(module, func, None)
            if not callable(fn):
                return f"⚠️ В '{mod}' нет функции '{func}'."
            try:
                result = fn()
                return result if result is not None else f"✅ Выполнено: {action}"
            except Exception as e:
                return f"⚠️ Ошибка при выполнении '{action}': {e}"

        # поиск функции по всем модулям
        for name, module in self.skills.items():
            fn = getattr(module, action, None)
            if callable(fn):
                try:
                    result = fn()
                    return result if result is not None else f"✅ Выполнено: {action}"
                except Exception as e:
                    return f"⚠️ Ошибка выполнения '{action}': {e}"

        return f"❌ Действие '{action}' не найдено."

    @lru_cache(maxsize=32)
    def list_skills(self):
        """Возвращает список всех загруженных навыков."""
        return list(self.skills.keys())
