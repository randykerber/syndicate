import os
import yaml
from dotenv import load_dotenv
from pathlib import Path

# Load secrets from .env
load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / '.env')

# Load project config from config.yaml
def load_config():
    config_path = Path(__file__).resolve().parents[2] / "conf" / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)
