"""
SOSAI -- Configuration
Stocke et charge la config depuis ~/.sosai/config.yaml
"""

import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

CONFIG_PATH = Path.home() / ".sosai" / "config.yaml"


@dataclass
class SOSAIConfig:
    owner_name:               str  = "Anonymous"
    owner_github:             str  = ""
    model_id:                 str  = "llama-3.3-70b-versatile"
    provider:                 str  = "groq"
    api_key:                  str  = ""
    model_type:               str  = "open-source"
    model_precision:          str  = "unknown"
    role:                     str  = "researcher"
    knowledge_repo_url:       str  = ""
    github_token:             str  = ""
    require_human_validation: bool = True
    ir_enabled:               bool = True
    sosai_version:            str  = "0.1.0"


def load() -> SOSAIConfig:
    cfg = SOSAIConfig()
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            data = yaml.safe_load(f) or {}
        for k, v in data.items():
            if hasattr(cfg, k) and v is not None:
                setattr(cfg, k, v)
    # Env vars override
    env_keys = {
        "api_key":      f"{cfg.provider.upper()}_API_KEY",
        "github_token": "GITHUB_TOKEN",
    }
    for attr, env in env_keys.items():
        val = os.getenv(env)
        if val and not getattr(cfg, attr):
            setattr(cfg, attr, val)
    return cfg


def save(cfg: SOSAIConfig):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = asdict(cfg)
    # Ne jamais sauvegarder les tokens en clair
    data.pop("api_key", None)
    data.pop("github_token", None)
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


def exists() -> bool:
    return CONFIG_PATH.exists()
