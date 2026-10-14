from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.yaml"


def loadDefaultConfig():
    """Carga la configuración y resuelve las rutas desde la raíz del proyecto."""
    with CONFIG_PATH.open(encoding="utf-8") as f:
        config = yaml.safe_load(f)

    for key in ("timetable_path", "forms_data_path", "chromedriver_path", "chrome_data_dir"):
        path = Path(config[key])
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        config[key] = str(path)

    for key in ("timetable_path", "forms_data_path"):
        Path(config[key]).parent.mkdir(parents=True, exist_ok=True)

    return config
