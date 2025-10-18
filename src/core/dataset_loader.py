import yaml

def load_dataset(path="data/commands.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
