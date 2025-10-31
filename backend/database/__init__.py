"""Database package initialization"""

from .models import Base, User, Project, Generation, APIKey, Model
from .database import get_db, init_db, engine, SessionLocal
from .crud import (
    create_user, get_user, get_user_by_email,
    create_project, get_project, get_user_projects,
    create_generation, get_generation, get_project_generations,
    create_api_key, get_api_keys, delete_api_key,
    create_model, get_models, update_model_status
)

__all__ = [
    "Base", "User", "Project", "Generation", "APIKey", "Model",
    "get_db", "init_db", "engine", "SessionLocal",
    "create_user", "get_user", "get_user_by_email",
    "create_project", "get_project", "get_user_projects",
    "create_generation", "get_generation", "get_project_generations",
    "create_api_key", "get_api_keys", "delete_api_key",
    "create_model", "get_models", "update_model_status"
]
