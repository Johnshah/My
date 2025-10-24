"""
Code Generator Service
Generates actual code for different parts of the application
"""

import os
import logging
from typing import Dict, List, Any
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class CodeGenerator:
    """Generates code for different app components"""
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / "templates"
        self.output_dir = Path("/tmp/my_generated")
        self.output_dir.mkdir(exist_ok=True, parents=True)
    
    async def generate_full_app(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete app code from plan"""
        logger.info("Generating full app code...")
        
        code = {
            "frontend": await self._generate_frontend(plan),
            "backend": await self._generate_backend(plan),
            "database": await self._generate_database(plan),
            "config": await self._generate_config(plan),
            "tests": await self._generate_tests(plan),
            "docs": await self._generate_docs(plan)
        }
        
        return code
    
    async def _generate_frontend(self, plan: Dict[str, Any]) -> Dict[str, str]:
        """Generate frontend code"""
        frontend_code = {}
        
        # Generate Next.js pages
        frontend_code["pages/index.tsx"] = self._template_nextjs_page(
            "Home",
            "Welcome to your app",
            plan.get("ui_components", [])
        )
        
        frontend_code["pages/_app.tsx"] = '''import type { AppProps } from 'next/app'
import '../styles/globals.css'

export default function App({ Component, pageProps }: AppProps) {
  return <Component {...pageProps} />
}
'''
        
        frontend_code["pages/api/hello.ts"] = '''import type { NextApiRequest, NextApiResponse } from 'next'

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  res.status(200).json({ message: 'Hello from My!' })
}
'''
        
        # Generate components
        for component in plan.get("ui_components", [])[:3]:
            comp_name = component.get("name", "Component")
            frontend_code[f"components/{comp_name}.tsx"] = self._template_react_component(comp_name)
        
        # Package.json
        frontend_code["package.json"] = json.dumps({
            "name": "my-generated-app",
            "version": "1.0.0",
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start"
            },
            "dependencies": {
                "next": "14.0.0",
                "react": "18.2.0",
                "react-dom": "18.2.0",
                "tailwindcss": "3.3.0"
            }
        }, indent=2)
        
        return frontend_code
    
    async def _generate_backend(self, plan: Dict[str, Any]) -> Dict[str, str]:
        """Generate backend code"""
        backend_code = {}
        
        # Main FastAPI app
        backend_code["main.py"] = '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="My Generated App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to your generated API!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
'''
        
        # Generate API routes
        for endpoint in plan.get("api_endpoints", [])[:5]:
            method = endpoint.get("method", "GET").lower()
            path = endpoint.get("path", "/api/items")
            
        backend_code["requirements.txt"] = '''fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
'''
        
        return backend_code
    
    async def _generate_database(self, plan: Dict[str, Any]) -> Dict[str, str]:
        """Generate database models and migrations"""
        db_code = {}
        
        db_code["models.py"] = '''from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
'''
        
        return db_code
    
    async def _generate_config(self, plan: Dict[str, Any]) -> Dict[str, str]:
        """Generate configuration files"""
        config = {}
        
        config["Dockerfile"] = '''FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
        
        config["docker-compose.yml"] = '''version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
'''
        
        config[".env.example"] = '''DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-secret-key-here
'''
        
        return config
    
    async def _generate_tests(self, plan: Dict[str, Any]) -> Dict[str, str]:
        """Generate test files"""
        tests = {}
        
        tests["test_main.py"] = '''import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
'''
        
        return tests
    
    async def _generate_docs(self, plan: Dict[str, Any]) -> Dict[str, str]:
        """Generate documentation"""
        docs = {}
        
        docs["README.md"] = f'''# My Generated App

## Description
{plan.get("user_prompt", "A generated application")}

## Tech Stack
- Frontend: React, Next.js, TailwindCSS
- Backend: FastAPI, Python
- Database: PostgreSQL/SQLite

## Getting Started

### Development
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Generated by My - Universal AI App Generator
'''
        
        return docs
    
    def _template_nextjs_page(self, title: str, description: str, components: List[Dict]) -> str:
        """Template for Next.js page"""
        return f'''export default function {title}Page() {{
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-4xl font-bold mb-4">{title}</h1>
      <p className="text-lg">{description}</p>
    </div>
  )
}}
'''
    
    def _template_react_component(self, name: str) -> str:
        """Template for React component"""
        return f'''interface {name}Props {{
  // Add props here
}}

export default function {name}({{ }}: {name}Props) {{
  return (
    <div className="component-{name.lower()}">
      <h2>{name}</h2>
    </div>
  )
}}
'''
    
    async def create_project_structure(self, project_id: str, code: Dict[str, Any]) -> str:
        """Create actual project files from generated code"""
        project_path = self.output_dir / project_id
        project_path.mkdir(exist_ok=True, parents=True)
        
        # Write all code files
        for section, files in code.items():
            section_path = project_path / section
            section_path.mkdir(exist_ok=True, parents=True)
            
            for file_path, content in files.items():
                full_path = section_path / file_path
                full_path.parent.mkdir(exist_ok=True, parents=True)
                
                with open(full_path, 'w') as f:
                    f.write(content)
        
        logger.info(f"Project structure created at {project_path}")
        return str(project_path)
