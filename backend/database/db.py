"""
Database Service
Handles all database operations using SQLite/SQLAlchemy
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import asyncio
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)

class Database:
    """Simple file-based database for development"""
    
    def __init__(self):
        self.db_dir = Path("/tmp/my_database")
        self.db_dir.mkdir(exist_ok=True, parents=True)
        self.projects_file = self.db_dir / "projects.json"
        self.builds_file = self.db_dir / "builds.json"
        
        self.projects = {}
        self.builds = {}
    
    async def initialize(self):
        """Initialize database"""
        logger.info("Initializing database...")
        
        # Load existing data
        if self.projects_file.exists():
            with open(self.projects_file, 'r') as f:
                self.projects = json.load(f)
        
        if self.builds_file.exists():
            with open(self.builds_file, 'r') as f:
                self.builds = json.load(f)
        
        logger.info(f"Database initialized with {len(self.projects)} projects and {len(self.builds)} builds")
    
    async def health_check(self) -> bool:
        """Check database health"""
        return self.db_dir.exists()
    
    async def create_project(self, data: Dict[str, Any]) -> str:
        """Create a new project"""
        project_id = str(uuid.uuid4())
        
        project = {
            "id": project_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            **data
        }
        
        self.projects[project_id] = project
        await self._save_projects()
        
        logger.info(f"Created project {project_id}")
        return project_id
    
    async def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project by ID"""
        return self.projects.get(project_id)
    
    async def update_project(self, project_id: str, data: Dict[str, Any]):
        """Update project"""
        if project_id in self.projects:
            self.projects[project_id].update(data)
            self.projects[project_id]["updated_at"] = datetime.utcnow().isoformat()
            await self._save_projects()
            logger.info(f"Updated project {project_id}")
    
    async def list_projects(self, skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        """List all projects"""
        all_projects = list(self.projects.values())
        # Sort by created_at desc
        all_projects.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return all_projects[skip:skip+limit]
    
    async def delete_project(self, project_id: str):
        """Delete project"""
        if project_id in self.projects:
            del self.projects[project_id]
            await self._save_projects()
            logger.info(f"Deleted project {project_id}")
    
    async def create_build(self, data: Dict[str, Any]) -> str:
        """Create a new build"""
        build_id = str(uuid.uuid4())
        
        build = {
            "id": build_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            **data
        }
        
        self.builds[build_id] = build
        await self._save_builds()
        
        logger.info(f"Created build {build_id}")
        return build_id
    
    async def get_build(self, build_id: str) -> Optional[Dict[str, Any]]:
        """Get build by ID"""
        return self.builds.get(build_id)
    
    async def update_build(self, build_id: str, data: Dict[str, Any]):
        """Update build"""
        if build_id in self.builds:
            self.builds[build_id].update(data)
            self.builds[build_id]["updated_at"] = datetime.utcnow().isoformat()
            await self._save_builds()
            logger.info(f"Updated build {build_id}")
    
    async def _save_projects(self):
        """Save projects to file"""
        with open(self.projects_file, 'w') as f:
            json.dump(self.projects, f, indent=2)
    
    async def _save_builds(self):
        """Save builds to file"""
        with open(self.builds_file, 'w') as f:
            json.dump(self.builds, f, indent=2)
    
    async def close(self):
        """Close database connections"""
        logger.info("Closing database...")
        await self._save_projects()
        await self._save_builds()
