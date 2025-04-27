import yaml
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / 'config.yaml'
COMMANDS_PATH = BASE_DIR / 'commands.yaml'


class Config:
    def __init__(self):
        with open(CONFIG_PATH, encoding='utf-8') as file:
            self.data = yaml.safe_load(file)
        with open(COMMANDS_PATH, encoding='utf-8') as file:
            self.commands = yaml.safe_load(file)

    def get(self, key: str, default=None):
        return self.data.get(key, default)
    
    def get_commands(self):
        return self.commands
    
config = Config()
