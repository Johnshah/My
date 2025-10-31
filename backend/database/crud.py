"""
CRUD (Create, Read, Update, Delete) operations for database models
All operations are async-compatible and include error handling
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from passlib.context import CryptContext

from .models import (
    User, Project, Generation, APIKey, Model, BuildCache,
    UserRole, ProjectStatus, AppComplexity, ModelType, ModelBackend
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================================================
# User Operations
# ============================================================================

def create_user(
    db: Session,
    email: str,
    username: str,
    password: str,
    full_name: Optional[str] = None,
    role: UserRole = UserRole.USER
) -> User:
    """Create a new user"""
    hashed_password = pwd_context.hash(password)
    user = User(
        email=email,
        username=username,
        hashed_password=hashed_password,
        full_name=full_name,
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def update_user_login(db: Session, user_id: int):
    """Update user's last login time"""
    user = get_user(db, user_id)
    if user:
        user.last_login = datetime.utcnow()
        db.commit()


def update_user_preferences(db: Session, user_id: int, preferences: Dict[str, Any]):
    """Update user preferences"""
    user = get_user(db, user_id)
    if user:
        user.preferences = preferences
        db.commit()
        db.refresh(user)
    return user


# ============================================================================
# Project Operations
# ============================================================================

def create_project(
    db: Session,
    user_id: int,
    name: str,
    prompt: str,
    app_type: str = "full-stack",
    complexity: AppComplexity = AppComplexity.STANDARD,
    platforms: Optional[List[str]] = None,
    source_type: Optional[str] = None,
    source_url: Optional[str] = None,
    source_data: Optional[Dict[str, Any]] = None
) -> Project:
    """Create a new project"""
    project = Project(
        user_id=user_id,
        name=name,
        prompt=prompt,
        app_type=app_type,
        complexity=complexity,
        platforms=platforms or ["web"],
        source_type=source_type or "text_prompt",
        source_url=source_url,
        source_data=source_data or {}
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_project(db: Session, project_id: int) -> Optional[Project]:
    """Get project by ID"""
    return db.query(Project).filter(Project.id == project_id).first()


def get_user_projects(
    db: Session,
    user_id: int,
    status: Optional[ProjectStatus] = None,
    limit: int = 50,
    offset: int = 0
) -> List[Project]:
    """Get all projects for a user"""
    query = db.query(Project).filter(Project.user_id == user_id)
    
    if status:
        query = query.filter(Project.status == status)
    
    return query.order_by(desc(Project.created_at)).limit(limit).offset(offset).all()


def update_project_status(
    db: Session,
    project_id: int,
    status: ProjectStatus,
    progress: Optional[int] = None,
    current_phase: Optional[str] = None,
    error_message: Optional[str] = None
):
    """Update project status and progress"""
    project = get_project(db, project_id)
    if project:
        project.status = status
        if progress is not None:
            project.progress = progress
        if current_phase:
            project.current_phase = current_phase
        if error_message:
            project.error_message = error_message
        
        # Set timestamps
        if status == ProjectStatus.GENERATING and not project.started_at:
            project.started_at = datetime.utcnow()
        elif status in [ProjectStatus.COMPLETED, ProjectStatus.FAILED]:
            project.completed_at = datetime.utcnow()
            if project.started_at:
                project.actual_time = int((project.completed_at - project.started_at).total_seconds())
        
        db.commit()
        db.refresh(project)
    return project


def update_project_results(
    db: Session,
    project_id: int,
    output_path: Optional[str] = None,
    repository_url: Optional[str] = None,
    download_url: Optional[str] = None,
    file_count: Optional[int] = None,
    line_count: Optional[int] = None,
    build_logs: Optional[List[Dict]] = None
):
    """Update project results"""
    project = get_project(db, project_id)
    if project:
        if output_path:
            project.output_path = output_path
        if repository_url:
            project.repository_url = repository_url
        if download_url:
            project.download_url = download_url
        if file_count is not None:
            project.file_count = file_count
        if line_count is not None:
            project.line_count = line_count
        if build_logs:
            project.build_logs = build_logs
        
        db.commit()
        db.refresh(project)
    return project


def delete_project(db: Session, project_id: int) -> bool:
    """Delete a project"""
    project = get_project(db, project_id)
    if project:
        db.delete(project)
        db.commit()
        return True
    return False


# ============================================================================
# Generation Operations
# ============================================================================

def create_generation(
    db: Session,
    project_id: int,
    generation_type: str = "initial",
    config: Optional[Dict[str, Any]] = None
) -> Generation:
    """Create a new generation attempt"""
    generation = Generation(
        project_id=project_id,
        generation_type=generation_type,
        config=config or {}
    )
    db.add(generation)
    db.commit()
    db.refresh(generation)
    return generation


def get_generation(db: Session, generation_id: int) -> Optional[Generation]:
    """Get generation by ID"""
    return db.query(Generation).filter(Generation.id == generation_id).first()


def get_project_generations(db: Session, project_id: int) -> List[Generation]:
    """Get all generation attempts for a project"""
    return db.query(Generation).filter(
        Generation.project_id == project_id
    ).order_by(desc(Generation.created_at)).all()


def update_generation_status(
    db: Session,
    generation_id: int,
    status: ProjectStatus,
    progress: Optional[int] = None,
    error_message: Optional[str] = None
):
    """Update generation status"""
    generation = get_generation(db, generation_id)
    if generation:
        generation.status = status
        if progress is not None:
            generation.progress = progress
        if error_message:
            generation.error_message = error_message
        
        if status == ProjectStatus.GENERATING and not generation.started_at:
            generation.started_at = datetime.utcnow()
        elif status in [ProjectStatus.COMPLETED, ProjectStatus.FAILED]:
            generation.completed_at = datetime.utcnow()
            if generation.started_at:
                generation.total_time = int((generation.completed_at - generation.started_at).total_seconds())
        
        db.commit()
        db.refresh(generation)
    return generation


def update_generation_results(
    db: Session,
    generation_id: int,
    output_data: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    models_used: Optional[List[str]] = None,
    logs: Optional[List[Dict]] = None
):
    """Update generation results"""
    generation = get_generation(db, generation_id)
    if generation:
        if output_data:
            generation.output_data = output_data
        if metrics:
            generation.metrics = metrics
        if models_used:
            generation.models_used = models_used
        if logs:
            generation.logs = logs
        
        db.commit()
        db.refresh(generation)
    return generation


# ============================================================================
# API Key Operations
# ============================================================================

def create_api_key(
    db: Session,
    user_id: int,
    service: str,
    key_name: str,
    encrypted_key: str
) -> APIKey:
    """Create a new API key"""
    api_key = APIKey(
        user_id=user_id,
        service=service,
        key_name=key_name,
        encrypted_key=encrypted_key
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return api_key


def get_api_keys(db: Session, user_id: int, service: Optional[str] = None) -> List[APIKey]:
    """Get user's API keys"""
    query = db.query(APIKey).filter(APIKey.user_id == user_id, APIKey.is_active == True)
    
    if service:
        query = query.filter(APIKey.service == service)
    
    return query.all()


def update_api_key_usage(db: Session, key_id: int):
    """Update API key usage"""
    api_key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if api_key:
        api_key.usage_count += 1
        api_key.last_used = datetime.utcnow()
        db.commit()


def delete_api_key(db: Session, key_id: int) -> bool:
    """Delete an API key"""
    api_key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if api_key:
        db.delete(api_key)
        db.commit()
        return True
    return False


# ============================================================================
# Model Operations
# ============================================================================

def create_model(
    db: Session,
    name: str,
    display_name: str,
    model_type: ModelType,
    backend: ModelBackend,
    **kwargs
) -> Model:
    """Create a new model entry"""
    model = Model(
        name=name,
        display_name=display_name,
        model_type=model_type,
        backend=backend,
        **kwargs
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


def get_models(
    db: Session,
    model_type: Optional[ModelType] = None,
    backend: Optional[ModelBackend] = None,
    available_only: bool = False
) -> List[Model]:
    """Get models with optional filtering"""
    query = db.query(Model)
    
    if model_type:
        query = query.filter(Model.model_type == model_type)
    if backend:
        query = query.filter(Model.backend == backend)
    if available_only:
        query = query.filter(Model.is_available == True)
    
    return query.all()


def get_model_by_name(db: Session, name: str) -> Optional[Model]:
    """Get model by name"""
    return db.query(Model).filter(Model.name == name).first()


def update_model_status(
    db: Session,
    model_id: int,
    is_downloaded: Optional[bool] = None,
    download_progress: Optional[int] = None,
    is_available: Optional[bool] = None
):
    """Update model status"""
    model = db.query(Model).filter(Model.id == model_id).first()
    if model:
        if is_downloaded is not None:
            model.is_downloaded = is_downloaded
        if download_progress is not None:
            model.download_progress = download_progress
        if is_available is not None:
            model.is_available = is_available
        
        db.commit()
        db.refresh(model)
    return model


def update_model_usage(db: Session, model_id: int):
    """Update model usage statistics"""
    model = db.query(Model).filter(Model.id == model_id).first()
    if model:
        model.usage_count += 1
        model.last_used = datetime.utcnow()
        db.commit()


# ============================================================================
# Build Cache Operations
# ============================================================================

def get_cache(db: Session, cache_key: str) -> Optional[BuildCache]:
    """Get cached data by key"""
    cache = db.query(BuildCache).filter(BuildCache.cache_key == cache_key).first()
    if cache:
        cache.hit_count += 1
        cache.last_accessed = datetime.utcnow()
        db.commit()
    return cache


def set_cache(
    db: Session,
    cache_key: str,
    data: Dict[str, Any],
    cache_type: str,
    content_hash: Optional[str] = None,
    file_path: Optional[str] = None,
    expires_at: Optional[datetime] = None
) -> BuildCache:
    """Set cached data"""
    cache = get_cache(db, cache_key)
    
    if cache:
        # Update existing cache
        cache.data = data
        cache.content_hash = content_hash
        cache.file_path = file_path
        cache.expires_at = expires_at
        cache.last_accessed = datetime.utcnow()
    else:
        # Create new cache
        cache = BuildCache(
            cache_key=cache_key,
            data=data,
            cache_type=cache_type,
            content_hash=content_hash,
            file_path=file_path,
            expires_at=expires_at
        )
        db.add(cache)
    
    db.commit()
    db.refresh(cache)
    return cache


def delete_expired_cache(db: Session):
    """Delete expired cache entries"""
    now = datetime.utcnow()
    db.query(BuildCache).filter(
        BuildCache.expires_at.isnot(None),
        BuildCache.expires_at < now
    ).delete()
    db.commit()
