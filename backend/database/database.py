"""
Database configuration and session management
Supports both SQLite (development) and PostgreSQL (production)
"""

import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging

from .models import Base

logger = logging.getLogger(__name__)

# Database URL from environment or default to SQLite
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./universal_ai_app_generator.db"
)

# Handle PostgreSQL URLs from Heroku/Railway
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite-specific settings
connect_args = {}
poolclass = None

if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    poolclass = StaticPool
    logger.info("Using SQLite database")
else:
    logger.info(f"Using PostgreSQL database: {DATABASE_URL.split('@')[-1]}")

# Create engine
engine_kwargs = {
    "connect_args": connect_args,
    "echo": os.getenv("SQL_ECHO", "false").lower() == "true",  # Log SQL queries
}

if poolclass:
    engine_kwargs["poolclass"] = poolclass

engine = create_engine(DATABASE_URL, **engine_kwargs)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def init_db():
    """Initialize database - create all tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
        
        # Seed initial data if needed
        _seed_initial_data()
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def _seed_initial_data():
    """Seed database with initial models and configuration"""
    from .models import Model, ModelType, ModelBackend
    
    db = SessionLocal()
    try:
        # Check if models already exist
        existing_models = db.query(Model).count()
        if existing_models > 0:
            return
        
        # Seed AI models
        initial_models = [
            # Code Generation Models
            Model(
                name="deepseek-coder-6.7b",
                display_name="DeepSeek Coder 6.7B",
                description="Fast and efficient code generation model optimized for local deployment",
                model_type=ModelType.CODE_GENERATION,
                backend=ModelBackend.OLLAMA,
                model_id="deepseek-coder:6.7b",
                min_ram_gb=8,
                disk_size_gb=3.8,
                requires_gpu=False,
                is_available=True
            ),
            Model(
                name="codellama-7b",
                display_name="Code Llama 7B",
                description="Meta's Code Llama model for code generation and understanding",
                model_type=ModelType.CODE_GENERATION,
                backend=ModelBackend.OLLAMA,
                model_id="codellama:7b",
                min_ram_gb=8,
                disk_size_gb=3.8,
                requires_gpu=False,
                is_available=True
            ),
            Model(
                name="codellama-13b",
                display_name="Code Llama 13B",
                description="Larger Code Llama model for better code generation",
                model_type=ModelType.CODE_GENERATION,
                backend=ModelBackend.OLLAMA,
                model_id="codellama:13b",
                min_ram_gb=16,
                disk_size_gb=7.4,
                requires_gpu=True,
                is_available=True
            ),
            Model(
                name="mistral-7b-instruct",
                display_name="Mistral 7B Instruct",
                description="Mistral AI's instruction-tuned model for coding tasks",
                model_type=ModelType.CODE_GENERATION,
                backend=ModelBackend.OLLAMA,
                model_id="mistral:7b-instruct",
                min_ram_gb=8,
                disk_size_gb=4.1,
                requires_gpu=False,
                is_available=True
            ),
            
            # Cloud Code Generation
            Model(
                name="gpt-4-turbo",
                display_name="GPT-4 Turbo",
                description="OpenAI's most capable model for code generation",
                model_type=ModelType.CODE_GENERATION,
                backend=ModelBackend.OPENAI,
                model_id="gpt-4-turbo-preview",
                requires_gpu=False,
                is_available=True
            ),
            Model(
                name="claude-3-opus",
                display_name="Claude 3 Opus",
                description="Anthropic's most capable model for complex coding tasks",
                model_type=ModelType.CODE_GENERATION,
                backend=ModelBackend.HUGGINGFACE,
                model_id="anthropic/claude-3-opus",
                requires_gpu=False,
                is_available=True
            ),
            
            # Speech to Text
            Model(
                name="whisper-base",
                display_name="Whisper Base",
                description="OpenAI Whisper base model for speech recognition",
                model_type=ModelType.SPEECH_TO_TEXT,
                backend=ModelBackend.TRANSFORMERS,
                model_id="openai/whisper-base",
                min_ram_gb=4,
                disk_size_gb=0.29,
                requires_gpu=False,
                is_available=True
            ),
            Model(
                name="whisper-medium",
                display_name="Whisper Medium",
                description="OpenAI Whisper medium model for better accuracy",
                model_type=ModelType.SPEECH_TO_TEXT,
                backend=ModelBackend.TRANSFORMERS,
                model_id="openai/whisper-medium",
                min_ram_gb=8,
                disk_size_gb=1.5,
                requires_gpu=True,
                is_available=True
            ),
            
            # Text to Speech
            Model(
                name="tts-xtts-v2",
                display_name="XTTS v2",
                description="Coqui XTTS v2 for high-quality multilingual TTS",
                model_type=ModelType.TEXT_TO_SPEECH,
                backend=ModelBackend.TRANSFORMERS,
                model_id="tts_models/multilingual/multi-dataset/xtts_v2",
                min_ram_gb=4,
                disk_size_gb=1.8,
                requires_gpu=False,
                is_available=True
            ),
            
            # Image Generation
            Model(
                name="stable-diffusion-xl",
                display_name="Stable Diffusion XL",
                description="High-quality image generation model",
                model_type=ModelType.IMAGE_GENERATION,
                backend=ModelBackend.TRANSFORMERS,
                model_id="stabilityai/stable-diffusion-xl-base-1.0",
                min_ram_gb=16,
                min_vram_gb=8,
                disk_size_gb=6.9,
                requires_gpu=True,
                is_available=True
            ),
        ]
        
        db.add_all(initial_models)
        db.commit()
        logger.info(f"Seeded {len(initial_models)} initial models")
        
    except Exception as e:
        logger.error(f"Failed to seed initial data: {e}")
        db.rollback()
    finally:
        db.close()


def get_db() -> Generator[Session, None, None]:
    """
    Get database session
    Use with FastAPI Depends:
        @app.get("/")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def reset_db():
    """Drop all tables and recreate - USE WITH CAUTION!"""
    logger.warning("Resetting database - all data will be lost!")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    logger.info("Database reset complete")
