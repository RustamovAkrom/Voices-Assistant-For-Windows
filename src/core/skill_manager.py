import importlib
import os
from pathlib import Path


class SkillManager:
    """
    Гибкий загрузчик навыков (skills/).
    Теперь поддерживает вложенные директории и пакеты (__init__.py).
    Пример структуры:
        src/skills/system/__init__.py
        src/skills/system/browser.py
        src/skills/music/player.py
    """

    def __init__(self, skills_path: str = "src/skills", debug: bool = True, context: dict = None):
        self.skills_path = Path(skills_path)
        self.debug = debug
        self.skills = {}
        self.context = context or {}
        self.load_all_skills()

    def log(self, *args):
        if self.debug:
            print("[SkillManager]", *args)

    def reload(self):
        """Полная перезагрузка всех модулей"""
        importlib.invalidate_caches()
        self.load_all_skills()
        self.log("🔄 Все навыки перезагружены.")

    def load_all_skills(self):
        """Рекурсивно загружает все Python-модули и пакеты в src/skills"""
        self.skills.clear()

        if not self.skills_path.exists():
            self.log(f"❌ Папка с навыками не найдена: {self.skills_path}")
            return

        importlib.invalidate_caches()

        for path in self.skills_path.rglob("*.py"):
            if path.name == "__init__.py":
                continue

            rel_path = path.relative_to(self.skills_path).with_suffix("")
            module_name = f"src.skills.{'.'.join(rel_path.parts)}"

            try:
                module = importlib.import_module(module_name)
                importlib.reload(module)
                self.skills[module_name] = module
                self.log(f"✅ Загружен модуль: {module_name}")
            except Exception as e:
                self.log(f"❌ Ошибка загрузки {module_name}: {e}")

    def execute(self, action: str, text: str = None):
        """
        Выполняет действие вида:
            system.browser.open_browser
            music.play
            utils.clear_cache
        """
        if not action:
            return "⚠️ Действие не указано."

        parts = action.split(".")
        module_name = None
        func_name = None

        # Пробуем найти полное совпадение модуля
        for i in range(len(parts) - 1, 0, -1):
            possible_module = f"src.skills.{'.'.join(parts[:i])}"
            if possible_module in self.skills:
                module_name = possible_module
                func_name = ".".join(parts[i:])
                break

        if not module_name:
            return f"⚠️ Не найден модуль для действия '{action}'."

        module = self.skills[module_name]
        func = module
        for attr in func_name.split("."):
            func = getattr(func, attr, None)
            if func is None:
                return f"⚠️ В модуле {module_name} нет функции '{func_name}'."

        if callable(func):
            try:
                return func(action=action, text=text, **self.context)
            except Exception as e:
                return f"⚠️ Ошибка при вызове {action}: {e}"

        return f"⚠️ '{func_name}' не является функцией."

    def list_skills(self):
        """Возвращает список всех загруженных модулей навыков."""
        return list(self.skills.keys())


# import importlib
# import os
# from pathlib import Path
# from functools import lru_cache


# class SkillManager:
#     """
#     Гибкий менеджер навыков.
#     Автоматически загружает, обновляет и вызывает функции из src/skills.
#     Поддерживает передачу аргументов, языка и контекста ассистента.
#     """

#     def __init__(self, skills_path: str = "src/skills", debug: bool = True, context: dict = None):
#         self.skills_path = Path(skills_path)
#         self.debug = debug
#         self.skills = {}
#         self.context = context or {}
#         self.load_all_skills()

#     def log(self, message: str):
#         if self.debug:
#             print(f"[DEBUG SkillManager] {message}")

#     # ========================= ЗАГРУЗКА НАВЫКОВ =========================

#     def load_all_skills(self):
#         """Загружает все навыки из директории src/skills."""
#         self.skills.clear()

#         if not self.skills_path.exists():
#             self.log(f"❌ Директория навыков не найдена: {self.skills_path}")
#             return

#         for file in os.listdir(self.skills_path):
#             if file.endswith(".py") and file != "__init__.py":
#                 name = file[:-3]
#                 module_name = f"src.skills.{name}"

#                 try:
#                     module = importlib.import_module(module_name)
#                     importlib.reload(module)
#                     self.skills[name] = module
#                     self.log(f"✅ Загружен навык: {name}")
#                 except Exception as e:
#                     print(f"[ERROR] Не удалось загрузить навык '{name}': {e}")

#     def reload(self):
#         """Перезагружает все навыки (например, после обновления файлов)."""
#         self.load_all_skills()
#         self.log("🔄 Все навыки перезагружены")

#     # ========================= ВЫПОЛНЕНИЕ ДЕЙСТВИЙ =========================

#     def execute(self, action: str, text: str = None):
#         """
#         Выполняет действие (например 'system.shutdown' или просто 'shutdown').
#         Передаёт функции все возможные данные: text, language, context, args, kwargs.
#         """
#         if not action:
#             return "⚠️ Действие не указано."
        
#         if not text:
#             return "⚠️ Text not found in SkillManager!"

#         # Собираем базовый контекст


#         def _call_function(fn):
#             context = {
#                 "action": action, 
#                 "text": text,
#                 **self.context,  # общий контекст (конфиг, имя пользователя, микрофон и т.п.)
#             }
#             try:
#                 return fn(**context)

#             except Exception as e:
#                 return f"⚠️ Ошибка при выполнении '{action}': {e}"

#         # Если указано module.function
#         if "." in action:
#             mod, func = action.split(".", 1)
#             module = self.skills.get(mod)

#             if not module:
#                 return f"❌ Навык '{mod}' не найден."

#             fn = getattr(module, func, None)
#             if not callable(fn):
#                 return f"⚠️ В '{mod}' нет функции '{func}'."

#             return _call_function(fn)

#         # Поиск по всем модулям
#         for name, module in self.skills.items():
#             fn = getattr(module, action, None)
#             if callable(fn):
#                 return _call_function(fn)

#         return f"❌ Действие '{action}' не найдено."

#     # ========================= СПРАВКА =========================

#     @lru_cache(maxsize=32)
#     def list_skills(self):
#         """Возвращает список всех загруженных навыков."""
#         return list(self.skills.keys())
