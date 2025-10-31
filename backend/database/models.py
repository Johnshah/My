"""
SQLAlchemy Database Models for Universal AI App Generator
Complete schema for users, projects, generations, API keys, and models
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, 
    ForeignKey, JSON, Float, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    """User roles"""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


class ProjectStatus(str, enum.Enum):
    """Project generation status"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    PLANNING = "planning"
    GENERATING = "generating"
    BUILDING = "building"
    TESTING = "testing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AppComplexity(str, enum.Enum):
    """App complexity levels"""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"


class ModelType(str, enum.Enum):
    """AI Model types"""
    CODE_GENERATION = "code_generation"
    CODE_ANALYSIS = "code_analysis"
    IMAGE_GENERATION = "image_generation"
    VIDEO_GENERATION = "video_generation"
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"


class ModelBackend(str, enum.Enum):
    """Model backend types"""
    OLLAMA = "ollama"
    TRANSFORMERS = "transformers"
    HUGGINGFACE = "huggingface"
    REPLICATE = "replicate"
    OPENAI = "openai"
    GOOGLE = "google"
    ELEVENLABS = "elevenlabs"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime)
    
    # Settings
    preferences = Column(JSON, default=dict)  # User preferences and settings
    
    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class Project(Base):
    """Project/App model"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text)
    app_type = Column(String(50))  # full-stack, frontend-only, backend-only, mobile, desktop
    complexity = Column(SQLEnum(AppComplexity), default=AppComplexity.STANDARD, nullable=False)
    
    # Source
    source_type = Column(String(50))  # github, upload, text_prompt
    source_url = Column(String(500))  # GitHub URL
    source_data = Column(JSON)  # Additional source data
    
    # Generation details
    prompt = Column(Text)  # User's text prompt
    platforms = Column(JSON, default=list)  # ["web", "android", "ios", "desktop"]
    features = Column(JSON, default=list)  # List of requested features
    tech_stack = Column(JSON, default=dict)  # Detected/selected technologies
    
    # Status
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.PENDING, nullable=False, index=True)
    progress = Column(Integer, default=0)  # 0-100
    current_phase = Column(String(100))  # Current generation phase
    error_message = Column(Text)
    
    # Results
    output_path = Column(String(500))  # Path to generated code
    repository_url = Column(String(500))  # GitHub repo URL if created
    download_url = Column(String(500))  # Download URL for zip file
    build_logs = Column(JSON, default=list)  # Build/generation logs
    
    # Metadata
    estimated_time = Column(Integer)  # Estimated time in seconds
    actual_time = Column(Integer)  # Actual generation time in seconds
    file_count = Column(Integer, default=0)
    line_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="projects")
    generations = relationship("Generation", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status}')>"


class Generation(Base):
    """Individual generation/build attempt"""
    __tablename__ = "generations"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    
    # Generation details
    generation_type = Column(String(50))  # initial, rebuild, update, fix
    config = Column(JSON, default=dict)  # Generation configuration
    models_used = Column(JSON, default=list)  # List of AI models used
    
    # Status
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.PENDING, nullable=False)
    progress = Column(Integer, default=0)
    error_message = Column(Text)
    
    # Results
    output_data = Column(JSON, default=dict)  # Generated files, stats, etc.
    metrics = Column(JSON, default=dict)  # Quality metrics, test coverage, etc.
    logs = Column(JSON, default=list)  # Detailed logs
    
    # Performance
    total_time = Column(Integer)  # Total time in seconds
    model_time = Column(Integer)  # Time spent on AI models
    build_time = Column(Integer)  # Time spent on building
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    project = relationship("Project", back_populates="generations")
    
    def __repr__(self):
        return f"<Generation(id={self.id}, project_id={self.project_id}, status='{self.status}')>"


class APIKey(Base):
    """API Keys for cloud services"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Key details
    service = Column(String(100), nullable=False)  # huggingface, replicate, openai, etc.
    key_name = Column(String(255), nullable=False)  # User-friendly name
    encrypted_key = Column(Text, nullable=False)  # Encrypted API key
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_valid = Column(Boolean, default=True, nullable=False)  # Validated status
    last_validated = Column(DateTime)
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    def __repr__(self):
        return f"<APIKey(id={self.id}, service='{self.service}', name='{self.key_name}')>"


class Model(Base):
    """AI Model registry"""
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Model details
    name = Column(String(255), nullable=False, unique=True, index=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text)
    model_type = Column(SQLEnum(ModelType), nullable=False, index=True)
    backend = Column(SQLEnum(ModelBackend), nullable=False)
    
    # Configuration
    model_id = Column(String(255))  # HuggingFace model ID, Ollama model name, etc.
    version = Column(String(100))
    parameters = Column(JSON, default=dict)  # Model-specific parameters
    
    # Requirements
    min_ram_gb = Column(Integer)  # Minimum RAM required
    min_vram_gb = Column(Integer)  # Minimum VRAM required
    disk_size_gb = Column(Float)  # Model size on disk
    requires_gpu = Column(Boolean, default=False)
    
    # Status
    is_available = Column(Boolean, default=True, nullable=False)
    is_downloaded = Column(Boolean, default=False, nullable=False)
    download_progress = Column(Integer, default=0)  # 0-100
    
    # Performance
    avg_generation_time = Column(Float)  # Average time in seconds
    tokens_per_second = Column(Float)
    quality_score = Column(Float)  # 0-100
    
    # Usage
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Model(id={self.id}, name='{self.name}', backend='{self.backend}')>"


class BuildCache(Base):
    """Cache for build artifacts and generated code"""
    __tablename__ = "build_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Cache key
    cache_key = Column(String(255), unique=True, index=True, nullable=False)
    content_hash = Column(String(64), index=True)  # SHA256 hash
    
    # Data
    data = Column(JSON)  # Cached data
    file_path = Column(String(500))  # Path to cached file
    
    # Metadata
    cache_type = Column(String(50))  # code, build, analysis, etc.
    size_bytes = Column(Integer)
    hit_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    def __repr__(self):
        return f"<BuildCache(id={self.id}, key='{self.cache_key}', type='{self.cache_type}')>"
