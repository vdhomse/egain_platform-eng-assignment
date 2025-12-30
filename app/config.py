import json
import os
from dataclasses import dataclass
from typing import Dict

@dataclass(frozen=True)
class Settings:
    db_path: str
    api_keys: Dict[str, str]  # tenant_id -> api_key

def load_settings() -> Settings:
    db_path = os.getenv("DB_PATH", "egain_knowledge.db")
    api_keys_json = os.getenv("API_KEYS_JSON", "{}")
    try:
        api_keys = json.loads(api_keys_json)
        if not isinstance(api_keys, dict):
            raise ValueError("API_KEYS_JSON must be a JSON object mapping tenantId -> apiKey")
        api_keys = {str(k): str(v) for k, v in api_keys.items()}
    except Exception as e:
        raise RuntimeError(f"Invalid API_KEYS_JSON: {e}")
    return Settings(db_path=db_path, api_keys=api_keys)
