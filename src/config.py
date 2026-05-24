import json
import os
from pathlib import Path
from pydantic import BaseModel

class DatabaseSecuritySettings(BaseModel):
    allow_insert: bool = False
    allow_update: bool = False
    allow_delete: bool = False
    allow_ddl: bool = False

class Config(BaseModel):
    allow_unsafe_local_fallback: bool = False
    tools_directory: str = "./dynamic_tools"
    workspace_directory: str = "./workspace"
    docker_image: str = "python:3.11-slim"
    database_security: DatabaseSecuritySettings = DatabaseSecuritySettings()

def load_config(config_path: str = "config.json") -> Config:
    # Resolve relative to the project root
    project_root = Path(__file__).parent.parent
    path = project_root / config_path
    
    if not path.exists():
        return Config()
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return Config(**data)

# Global configuration instance
settings = load_config()
