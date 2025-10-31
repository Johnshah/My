"""
Celery Application Configuration
Background task processing for AI app generation
"""

import os
from celery import Celery
from kombu import Exchange, Queue

# Redis URL from environment or default
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "universal_ai_app_generator",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "tasks.generation_tasks",
        "tasks.analysis_tasks",
        "tasks.build_tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task execution
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task routing
    task_routes={
        "tasks.generation_tasks.*": {"queue": "generation"},
        "tasks.analysis_tasks.*": {"queue": "analysis"},
        "tasks.build_tasks.*": {"queue": "builds"},
    },
    
    # Task time limits
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=3300,  # 55 minutes soft limit
    
    # Task results
    result_expires=86400,  # Results expire after 24 hours
    result_extended=True,
    
    # Worker configuration
    worker_prefetch_multiplier=1,  # One task at a time per worker
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks
    
    # Task retry policy
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Beat schedule (for periodic tasks)
    beat_schedule={
        "cleanup-expired-cache": {
            "task": "tasks.maintenance_tasks.cleanup_expired_cache",
            "schedule": 3600.0,  # Run every hour
        },
        "update-model-stats": {
            "task": "tasks.maintenance_tasks.update_model_stats",
            "schedule": 1800.0,  # Run every 30 minutes
        },
    },
)

# Define queues with priorities
celery_app.conf.task_queues = (
    Queue("generation", Exchange("generation"), routing_key="generation", priority=5),
    Queue("analysis", Exchange("analysis"), routing_key="analysis", priority=7),
    Queue("builds", Exchange("builds"), routing_key="builds", priority=3),
    Queue("celery", Exchange("celery"), routing_key="celery", priority=1),  # Default queue
)

# Task annotations
celery_app.conf.task_annotations = {
    "tasks.generation_tasks.generate_app": {
        "rate_limit": "10/m",  # Max 10 generation tasks per minute
        "time_limit": 1200,  # 20 minutes for generation
    },
    "tasks.generation_tasks.generate_app_deep_mode": {
        "rate_limit": "5/m",
        "time_limit": 3600,  # 1 hour for deep mode
    },
}

if __name__ == "__main__":
    celery_app.start()
