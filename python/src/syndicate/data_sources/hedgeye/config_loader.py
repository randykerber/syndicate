import os
import yaml
from dotenv import load_dotenv
from pathlib import Path

# Load secrets from .env (at python/ directory level)
load_dotenv(dotenv_path=Path(__file__).resolve().parents[4] / '.env')

# Load project config from config/hedgeye.yaml
def load_config():
    config_path = Path(__file__).resolve().parents[4] / "config" / "hedgeye.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)
