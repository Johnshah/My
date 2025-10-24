"""
GitHub Service
Handles all GitHub repository operations including:
- Cloning repositories
- Analyzing code structure
- Detecting tech stacks
- Extracting dependencies
"""

import os
import git
import zipfile
import tarfile
import shutil
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
import json
from github import Github, GithubException
import asyncio

logger = logging.getLogger(__name__)

class GitHubService:
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.github_client = Github(self.github_token) if self.github_token else None
        self.workspace_dir = Path("/tmp/my_workspace")
        self.workspace_dir.mkdir(exist_ok=True, parents=True)
    
    def is_configured(self) -> bool:
        """Check if GitHub integration is configured"""
        return self.github_client is not None
    
    async def clone_repo(self, repo_url: str, branch: str = "main") -> str:
        """
        Clone a GitHub repository
        
        Args:
            repo_url: GitHub repository URL
            branch: Branch to clone (default: main)
            
        Returns:
            Path to cloned repository
        """
        try:
            # Extract repo name from URL
            repo_name = repo_url.split("/")[-1].replace(".git", "")
            clone_path = self.workspace_dir / f"{repo_name}_{asyncio.get_event_loop().time()}"
            
            logger.info(f"Cloning repository {repo_url} to {clone_path}")
            
            # Clone repository
            await asyncio.to_thread(
                git.Repo.clone_from,
                repo_url,
                clone_path,
                branch=branch,
                depth=1  # Shallow clone for speed
            )
            
            logger.info(f"Successfully cloned repository to {clone_path}")
            return str(clone_path)
        
        except Exception as e:
            logger.error(f"Failed to clone repository: {str(e)}")
            raise Exception(f"Failed to clone repository: {str(e)}")
    
    async def analyze_repo(self, repo_path: str) -> Dict[str, Any]:
        """
        Analyze repository structure and content
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            Analysis results including file structure, languages, etc.
        """
        try:
            logger.info(f"Analyzing repository at {repo_path}")
            
            analysis = {
                "total_files": 0,
                "total_lines": 0,
                "file_types": {},
                "languages": {},
                "directory_structure": {},
                "entry_points": [],
                "config_files": [],
                "test_files": [],
                "documentation": []
            }
            
            # Walk through repository
            for root, dirs, files in os.walk(repo_path):
                # Skip common directories
                dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', 'venv', '.venv', 'dist', 'build']]
                
                for file in files:
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(repo_path)
                    
                    analysis["total_files"] += 1
                    
                    # Get file extension
                    ext = file_path.suffix.lower()
                    analysis["file_types"][ext] = analysis["file_types"].get(ext, 0) + 1
                    
                    # Identify entry points
                    if file in ['main.py', 'app.py', 'index.js', 'main.js', 'server.js', 'index.html']:
                        analysis["entry_points"].append(str(rel_path))
                    
                    # Identify config files
                    if file in ['package.json', 'requirements.txt', 'Dockerfile', 'docker-compose.yml', 
                               'setup.py', 'pyproject.toml', 'tsconfig.json', 'webpack.config.js', 
                               '.env.example', 'config.yml', 'config.json']:
                        analysis["config_files"].append(str(rel_path))
                    
                    # Identify test files
                    if 'test' in file.lower() or file.startswith('test_'):
                        analysis["test_files"].append(str(rel_path))
                    
                    # Identify documentation
                    if ext in ['.md', '.rst', '.txt'] or file.upper() in ['README', 'LICENSE', 'CHANGELOG']:
                        analysis["documentation"].append(str(rel_path))
                    
                    # Count lines of code
                    if ext in ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.go', '.rs', '.rb', '.php']:
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                lines = len(f.readlines())
                                analysis["total_lines"] += lines
                                
                                # Map language
                                lang_map = {
                                    '.py': 'Python',
                                    '.js': 'JavaScript',
                                    '.ts': 'TypeScript',
                                    '.jsx': 'React',
                                    '.tsx': 'React TypeScript',
                                    '.java': 'Java',
                                    '.cpp': 'C++',
                                    '.c': 'C',
                                    '.go': 'Go',
                                    '.rs': 'Rust',
                                    '.rb': 'Ruby',
                                    '.php': 'PHP'
                                }
                                lang = lang_map.get(ext, 'Other')
                                analysis["languages"][lang] = analysis["languages"].get(lang, 0) + lines
                        except Exception as e:
                            logger.warning(f"Could not read file {file_path}: {str(e)}")
            
            logger.info(f"Repository analysis complete: {analysis['total_files']} files, {analysis['total_lines']} lines")
            return analysis
        
        except Exception as e:
            logger.error(f"Failed to analyze repository: {str(e)}")
            raise Exception(f"Failed to analyze repository: {str(e)}")
    
    async def detect_tech_stack(self, repo_path: str) -> List[str]:
        """
        Detect the technology stack used in the repository
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            List of detected technologies
        """
        try:
            logger.info(f"Detecting tech stack for {repo_path}")
            
            tech_stack = set()
            repo_path = Path(repo_path)
            
            # Check for common files and frameworks
            checks = {
                'package.json': ['Node.js', 'npm'],
                'yarn.lock': ['Yarn'],
                'requirements.txt': ['Python'],
                'Pipfile': ['Python', 'Pipenv'],
                'pyproject.toml': ['Python', 'Poetry'],
                'Cargo.toml': ['Rust'],
                'go.mod': ['Go'],
                'pom.xml': ['Java', 'Maven'],
                'build.gradle': ['Java', 'Gradle'],
                'Gemfile': ['Ruby'],
                'composer.json': ['PHP', 'Composer'],
                'Dockerfile': ['Docker'],
                'docker-compose.yml': ['Docker Compose'],
                '.dockerignore': ['Docker'],
                'next.config.js': ['Next.js', 'React'],
                'nuxt.config.js': ['Nuxt.js', 'Vue'],
                'angular.json': ['Angular'],
                'vue.config.js': ['Vue'],
                'svelte.config.js': ['Svelte'],
                'tsconfig.json': ['TypeScript'],
                'webpack.config.js': ['Webpack'],
                'vite.config.js': ['Vite'],
                'rollup.config.js': ['Rollup'],
                'tailwind.config.js': ['Tailwind CSS'],
                'postcss.config.js': ['PostCSS'],
                '.babelrc': ['Babel'],
                '.eslintrc': ['ESLint'],
                'jest.config.js': ['Jest'],
                'pytest.ini': ['pytest'],
                'Makefile': ['Make'],
                'CMakeLists.txt': ['CMake'],
                'capacitor.config.json': ['Capacitor', 'Mobile'],
                'android/': ['Android'],
                'ios/': ['iOS'],
                'electron.js': ['Electron', 'Desktop'],
            }
            
            for file, techs in checks.items():
                if (repo_path / file).exists():
                    tech_stack.update(techs)
            
            # Check package.json for more details
            package_json = repo_path / 'package.json'
            if package_json.exists():
                try:
                    with open(package_json, 'r') as f:
                        data = json.load(f)
                        deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                        
                        framework_map = {
                            'react': 'React',
                            'vue': 'Vue.js',
                            'angular': 'Angular',
                            'svelte': 'Svelte',
                            'next': 'Next.js',
                            'nuxt': 'Nuxt.js',
                            'express': 'Express.js',
                            'fastify': 'Fastify',
                            'nestjs': 'NestJS',
                            'koa': 'Koa',
                            'gatsby': 'Gatsby',
                            'remix': 'Remix',
                            'astro': 'Astro',
                            'redux': 'Redux',
                            'mobx': 'MobX',
                            'graphql': 'GraphQL',
                            'apollo': 'Apollo',
                            'prisma': 'Prisma',
                            'typeorm': 'TypeORM',
                            'mongoose': 'Mongoose',
                            'sequelize': 'Sequelize',
                            'tailwindcss': 'Tailwind CSS',
                            'bootstrap': 'Bootstrap',
                            'material-ui': 'Material-UI',
                            'ant-design': 'Ant Design',
                            'chakra-ui': 'Chakra UI',
                            'electron': 'Electron',
                            'capacitor': 'Capacitor',
                            'react-native': 'React Native',
                            'expo': 'Expo',
                            'webpack': 'Webpack',
                            'vite': 'Vite',
                            'rollup': 'Rollup',
                            'esbuild': 'esbuild',
                            'jest': 'Jest',
                            'vitest': 'Vitest',
                            'cypress': 'Cypress',
                            'playwright': 'Playwright',
                            'storybook': 'Storybook',
                        }
                        
                        for dep in deps.keys():
                            for key, framework in framework_map.items():
                                if key in dep.lower():
                                    tech_stack.add(framework)
                except Exception as e:
                    logger.warning(f"Could not parse package.json: {str(e)}")
            
            # Check requirements.txt for Python frameworks
            requirements = repo_path / 'requirements.txt'
            if requirements.exists():
                try:
                    with open(requirements, 'r') as f:
                        content = f.read().lower()
                        
                        framework_map = {
                            'django': 'Django',
                            'flask': 'Flask',
                            'fastapi': 'FastAPI',
                            'pyramid': 'Pyramid',
                            'tornado': 'Tornado',
                            'celery': 'Celery',
                            'sqlalchemy': 'SQLAlchemy',
                            'pandas': 'Pandas',
                            'numpy': 'NumPy',
                            'scikit-learn': 'Scikit-learn',
                            'tensorflow': 'TensorFlow',
                            'pytorch': 'PyTorch',
                            'keras': 'Keras',
                            'streamlit': 'Streamlit',
                            'gradio': 'Gradio',
                        }
                        
                        for key, framework in framework_map.items():
                            if key in content:
                                tech_stack.add(framework)
                except Exception as e:
                    logger.warning(f"Could not parse requirements.txt: {str(e)}")
            
            result = sorted(list(tech_stack))
            logger.info(f"Detected tech stack: {result}")
            return result
        
        except Exception as e:
            logger.error(f"Failed to detect tech stack: {str(e)}")
            return []
    
    async def extract_dependencies(self, repo_path: str) -> Dict[str, List[str]]:
        """
        Extract dependencies from various package managers
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            Dictionary of dependencies by type
        """
        try:
            logger.info(f"Extracting dependencies from {repo_path}")
            
            dependencies = {
                "npm": [],
                "python": [],
                "rust": [],
                "go": [],
                "java": [],
                "ruby": [],
                "php": []
            }
            
            repo_path = Path(repo_path)
            
            # NPM dependencies
            package_json = repo_path / 'package.json'
            if package_json.exists():
                try:
                    with open(package_json, 'r') as f:
                        data = json.load(f)
                        deps = data.get('dependencies', {})
                        dev_deps = data.get('devDependencies', {})
                        dependencies["npm"] = [f"{k}@{v}" for k, v in {**deps, **dev_deps}.items()]
                except Exception as e:
                    logger.warning(f"Could not parse package.json: {str(e)}")
            
            # Python dependencies
            requirements = repo_path / 'requirements.txt'
            if requirements.exists():
                try:
                    with open(requirements, 'r') as f:
                        dependencies["python"] = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                except Exception as e:
                    logger.warning(f"Could not parse requirements.txt: {str(e)}")
            
            # Rust dependencies
            cargo_toml = repo_path / 'Cargo.toml'
            if cargo_toml.exists():
                try:
                    with open(cargo_toml, 'r') as f:
                        content = f.read()
                        # Simple parsing (would be better with a proper TOML parser)
                        in_deps = False
                        for line in content.split('\n'):
                            if '[dependencies]' in line:
                                in_deps = True
                                continue
                            if in_deps and line.strip() and not line.startswith('['):
                                dependencies["rust"].append(line.strip())
                            elif in_deps and line.startswith('['):
                                break
                except Exception as e:
                    logger.warning(f"Could not parse Cargo.toml: {str(e)}")
            
            # Go dependencies
            go_mod = repo_path / 'go.mod'
            if go_mod.exists():
                try:
                    with open(go_mod, 'r') as f:
                        content = f.read()
                        in_require = False
                        for line in content.split('\n'):
                            if 'require' in line and '(' in line:
                                in_require = True
                                continue
                            if in_require and line.strip() and ')' not in line:
                                dependencies["go"].append(line.strip())
                            elif in_require and ')' in line:
                                break
                            elif 'require' in line and '(' not in line:
                                # Single line require
                                dep = line.replace('require', '').strip()
                                if dep:
                                    dependencies["go"].append(dep)
                except Exception as e:
                    logger.warning(f"Could not parse go.mod: {str(e)}")
            
            logger.info(f"Extracted dependencies: {sum(len(v) for v in dependencies.values())} total")
            return dependencies
        
        except Exception as e:
            logger.error(f"Failed to extract dependencies: {str(e)}")
            return {}
    
    async def extract_archive(self, archive_path: str) -> str:
        """
        Extract ZIP or TAR archive
        
        Args:
            archive_path: Path to the archive file
            
        Returns:
            Path to extracted content
        """
        try:
            logger.info(f"Extracting archive {archive_path}")
            
            archive_path = Path(archive_path)
            extract_dir = self.workspace_dir / f"extracted_{asyncio.get_event_loop().time()}"
            extract_dir.mkdir(exist_ok=True, parents=True)
            
            if archive_path.suffix == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    await asyncio.to_thread(zip_ref.extractall, extract_dir)
            elif archive_path.suffix in ['.tar', '.tar.gz', '.tgz']:
                with tarfile.open(archive_path, 'r:*') as tar_ref:
                    await asyncio.to_thread(tar_ref.extractall, extract_dir)
            else:
                raise Exception(f"Unsupported archive format: {archive_path.suffix}")
            
            logger.info(f"Archive extracted to {extract_dir}")
            return str(extract_dir)
        
        except Exception as e:
            logger.error(f"Failed to extract archive: {str(e)}")
            raise Exception(f"Failed to extract archive: {str(e)}")
    
    def get_repo_info(self, repo_url: str) -> Optional[Dict[str, Any]]:
        """
        Get repository information from GitHub API
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Repository information or None
        """
        if not self.github_client:
            logger.warning("GitHub client not configured")
            return None
        
        try:
            # Extract owner and repo name from URL
            parts = repo_url.replace("https://github.com/", "").replace(".git", "").split("/")
            if len(parts) < 2:
                return None
            
            owner, repo_name = parts[0], parts[1]
            
            # Get repo from GitHub API
            repo = self.github_client.get_repo(f"{owner}/{repo_name}")
            
            return {
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "language": repo.language,
                "topics": repo.get_topics(),
                "default_branch": repo.default_branch,
                "created_at": repo.created_at.isoformat(),
                "updated_at": repo.updated_at.isoformat(),
                "homepage": repo.homepage,
                "license": repo.license.name if repo.license else None
            }
        
        except GithubException as e:
            logger.error(f"GitHub API error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error getting repo info: {str(e)}")
            return None
