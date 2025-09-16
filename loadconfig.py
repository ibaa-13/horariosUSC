import yaml

CONFIG_PATH = r"C:\Users\usuario\python\horarios\config.yaml"

def loadDefaultConfig():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config