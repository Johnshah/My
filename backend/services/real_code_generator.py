"""
Real Code Generator with AI Integration
Generates actual working code using AI models
"""

import os
import logging
from typing import Dict, List, Any
from pathlib import Path
import asyncio
from .model_manager import model_manager

logger = logging.getLogger(__name__)

class RealCodeGenerator:
    """Generates real, working code using AI models"""
    
    def __init__(self):
        self.model_manager = model_manager
        self.output_dir = Path("/tmp/my_generated")
        self.output_dir.mkdir(exist_ok=True, parents=True)
    
    async def generate_full_app(self, plan: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        """
        Generate complete application code using AI
        Returns structured code files
        """
        logger.info(f"🤖 Generating full app with AI (complexity: {plan.get('complexity', 'standard')})")
        
        code = {
            "frontend": await self._generate_frontend_code(plan),
            "backend": await self._generate_backend_code(plan),
            "database": await self._generate_database_code(plan),
            "tests": await self._generate_test_code(plan),
            "config": await self._generate_config_files(plan),
            "docs": await self._generate_documentation(plan)
        }
        
        logger.info(f"✅ Generated {sum(len(v) for v in code.values())} files")
        return code
    
    async def _generate_frontend_code(self, plan: Dict[str, Any]) -> Dict[str, str]:
        """Generate frontend code with AI"""
        frontend = {}
        complexity = plan.get('complexity', 'standard')
        
        # Generate main page
        logger.info("Generating frontend pages...")
        
        page_prompt = f"""Generate a Next.js index page for: {plan['user_prompt']}

Requirements:
- Use TypeScript and React 18
- Use TailwindCSS for styling
- Include {', '.join(plan.get('features', [])[:5])}
- Complexity level: {complexity}
- Modern, responsive design

Generate ONLY the TypeScript code for pages/index.tsx:"""
        
        index_page = await self.model_manager.generate_code(
            page_prompt,
            language="typescript",
            max_tokens=2000
        )
        frontend["pages/index.tsx"] = self._clean_code(index_page)
        
        # Generate API routes
        api_prompt = f"""Generate Next.js API route for: {plan['user_prompt']}

Create a handler for /api/items that:
- Supports GET, POST, PUT, DELETE
- Uses TypeScript
- Returns JSON responses
- Includes error handling

Generate ONLY the TypeScript code for pages/api/items.ts:"""
        
        api_route = await self.model_manager.generate_code(
            api_prompt,
            language="typescript",
            max_tokens=1500
        )
        frontend["pages/api/items.ts"] = self._clean_code(api_route)
        
        # Generate components
        for component in plan.get('ui_components', [])[:3]:
            comp_name = component.get('name', 'Component')
            
            comp_prompt = f"""Generate a React component named {comp_name} for: {component.get('type', 'display')}

Requirements:
- TypeScript
- Functional component with hooks
- TailwindCSS styling
- Props interface
- Responsive design

Generate ONLY the component code:"""
            
            comp_code = await self.model_manager.generate_code(
                comp_prompt,
                language="typescript",
                max_tokens=1000
            )
            frontend[f"components/{comp_name}.tsx"] = self._clean_code(comp_code)
        
        # Package.json
        frontend["package.json"] = self._generate_package_json(plan)
        
        # Tailwind config
        frontend["tailwind.config.js"] = '''module.exports = {
  content: ['./pages/**/*.{js,ts,jsx,tsx}', './components/**/*.{js,ts,jsx,tsx}'],
  theme: { extend: {} },
  plugins: [],
}'''
        
        return frontend
    
    async def _generate_backend_code(self, plan: Dict[str, Any]) -> Dict[str, str]:
        """Generate backend code with AI"""
        backend = {}
        complexity = plan.get('complexity', 'standard')
        
        # Generate main FastAPI app
        logger.info("Generating backend API...")
        
        main_prompt = f"""Generate a FastAPI application for: {plan['user_prompt']}

Requirements:
- FastAPI with async/await
- CORS middleware
- {complexity} complexity level
- Include endpoints: {', '.join(e['path'] for e in plan.get('api_endpoints', [])[:5])}
- Error handling
- Pydantic models
- SQLAlchemy database connection

Generate ONLY the main.py code:"""
        
        main_code = await self.model_manager.generate_code(
            main_prompt,
            language="python",
            max_tokens=2500
        )
        backend["main.py"] = self._clean_code(main_code)
        
        # Generate database models
        models_prompt = f"""Generate SQLAlchemy models for: {plan['user_prompt']}

Tables needed: {', '.join(t['name'] for t in plan.get('database_schema', {}).get('tables', []))}

Requirements:
- SQLAlchemy ORM
- UUID primary keys
- Timestamps (created_at, updated_at)
- Relationships if needed
- Complexity level: {complexity}

Generate ONLY the models.py code:"""
        
        models_code = await self.model_manager.generate_code(
            models_prompt,
            language="python",
            max_tokens=2000
        )
        backend["models.py"] = self._clean_code(models_code)
        
        # Generate CRUD operations
        crud_prompt = f"""Generate CRUD operations for the models

Requirements:
- Async functions
- SQLAlchemy async session
- Error handling
- Type hints
- Create, Read, Update, Delete operations

Generate ONLY the crud.py code:"""
        
        crud_code = await self.model_manager.generate_code(
            crud_prompt,
            language="python",
            max_tokens=2000
        )
        backend["crud.py"] = self._clean_code(crud_code)
        
        # Requirements.txt
        backend["requirements.txt"] = self._generate_requirements(plan)
        
        return backend
    
    async def _generate_database_code(self, plan: Dict[str, Any]) -> Dict[str, str]:
        """Generate database setup code"""
        database = {}
        
        db_prompt = f"""Generate database connection and session management

Requirements:
- Async SQLAlchemy
- Connection pooling
- Session management
- Environment variable configuration

Generate ONLY the database.py code:"""
        
        db_code = await self.model_manager.generate_code(
            db_prompt,
            language="python",
            max_tokens=1000
        )
        database["database.py"] = self._clean_code(db_code)
        
        # Alembic init
        database["alembic.ini"] = '''[alembic]
script_location = alembic
sqlalchemy.url = driver://user:pass@localhost/dbname

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
'''
        
        return database
    
    async def _generate_test_code(self, plan: Dict[str, Any]) -> Dict[str, str]:
        """Generate test code with AI"""
        tests = {}
        
        test_prompt = f"""Generate pytest tests for: {plan['user_prompt']}

Requirements:
- Pytest with async support
- FastAPI TestClient
- Test all main endpoints
- Mocking where needed
- Comprehensive coverage

Generate ONLY the test_main.py code:"""
        
        test_code = await self.model_manager.generate_code(
            test_prompt,
            language="python",
            max_tokens=2000
        )
        tests["test_main.py"] = self._clean_code(test_code)
        
        return tests
    
    async def _generate_config_files(self, plan: Dict[str, Any]) -> Dict[str, str]:
        """Generate configuration files"""
        config = {}
        
        # Dockerfile
        config["Dockerfile"] = f'''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
        
        # docker-compose.yml
        config["docker-compose.yml"] = f'''version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/myapp
    depends_on:
      - db
      
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
'''
        
        # .env.example
        config[".env.example"] = f'''DATABASE_URL=sqlite:///./app.db
SECRET_KEY=change-this-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
'''
        
        # .gitignore
        config[".gitignore"] = '''__pycache__/
*.pyc
.env
venv/
node_modules/
.next/
dist/
build/
*.log
.DS_Store
'''
        
        return config
    
    async def _generate_documentation(self, plan: Dict[str, Any]) -> Dict[str, str]:
        """Generate documentation"""
        docs = {}
        
        readme_prompt = f"""Generate a README.md for: {plan['user_prompt']}

Include:
- Project description
- Features list
- Installation instructions
- Usage guide
- API documentation
- Tech stack

Generate the complete README:"""
        
        readme = await self.model_manager.generate_code(
            readme_prompt,
            language="markdown",
            max_tokens=1500
        )
        docs["README.md"] = self._clean_code(readme)
        
        return docs
    
    def _clean_code(self, code: str) -> str:
        """Clean up generated code"""
        # Remove markdown code blocks if present
        if "```" in code:
            lines = code.split('\n')
            in_block = False
            cleaned = []
            for line in lines:
                if line.strip().startswith('```'):
                    in_block = not in_block
                    continue
                if in_block or not line.strip().startswith('```'):
                    cleaned.append(line)
            code = '\n'.join(cleaned)
        
        return code.strip()
    
    def _generate_package_json(self, plan: Dict[str, Any]) -> str:
        """Generate package.json"""
        return '''{
  "name": "my-generated-app",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.0.4",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "tailwindcss": "3.4.0",
    "autoprefixer": "10.4.16",
    "postcss": "8.4.32",
    "axios": "1.6.2"
  },
  "devDependencies": {
    "@types/node": "20.10.6",
    "@types/react": "18.2.45",
    "@types/react-dom": "18.2.18",
    "typescript": "5.3.3",
    "eslint": "8.56.0",
    "eslint-config-next": "14.0.4"
  }
}'''
    
    def _generate_requirements(self, plan: Dict[str, Any]) -> str:
        """Generate requirements.txt"""
        complexity = plan.get('complexity', 'standard')
        
        base_reqs = '''fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.3
sqlalchemy==2.0.23
alembic==1.13.0
python-dotenv==1.0.0
'''
        
        if complexity == 'standard':
            base_reqs += '''asyncpg==0.29.0
redis==5.0.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
'''
        
        if complexity == 'advanced':
            base_reqs += '''celery==5.3.4
elasticsearch==8.11.0
websockets==12.0
prometheus-client==0.19.0
'''
        
        return base_reqs
    
    async def create_project_structure(
        self,
        project_id: str,
        code: Dict[str, Dict[str, str]]
    ) -> str:
        """Create actual project files"""
        project_path = self.output_dir / project_id
        project_path.mkdir(exist_ok=True, parents=True)
        
        # Write all files
        for section, files in code.items():
            section_path = project_path / section
            section_path.mkdir(exist_ok=True, parents=True)
            
            for file_path, content in files.items():
                full_path = section_path / file_path
                full_path.parent.mkdir(exist_ok=True, parents=True)
                
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
        
        logger.info(f"✅ Project created at: {project_path}")
        return str(project_path)

# Global instance
real_code_generator = RealCodeGenerator()
