import base64
import importlib
import json
import os


def get_env_value(key: str, isSecret: bool = False, default=None):

    current_env = get_current_env()

    try:
        config_module = importlib.import_module(f"src.config.{current_env}")

        value = getattr(config_module, key, default)

        return value
    except (ImportError, AttributeError):
        return default

def get_current_env() -> str:
    
    env_type = os.getenv("ENV", "prod").lower()

    return env_type