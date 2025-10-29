"""
AI Orchestrator Service
Coordinates multiple AI models and agents to:
- Plan app architecture
- Generate code
- Coordinate multi-agent workflows
- Manage local and cloud models
"""

import os
import logging
from typing import Dict, List, Any, Optional
import asyncio
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class AIOrchestrator:
    """
    Central AI orchestration service
    Manages multiple AI models and coordinates their work
    """
    
    def __init__(self):
        self.local_models = {}
        self.cloud_models = {}
        self.agents = {}
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load AI configuration from environment and config files"""
        config = {
            "models": {
                "local": {
                    "ollama_url": os.getenv("OLLAMA_URL", "http://localhost:11434"),
                    "vllm_url": os.getenv("VLLM_URL", "http://localhost:8080"),
                    "llamacpp_path": os.getenv("LLAMACPP_PATH", "/usr/local/bin/llama-cpp"),
                },
                "cloud": {
                    "huggingface_token": os.getenv("HUGGINGFACE_TOKEN"),
                    "openai_key": os.getenv("OPENAI_API_KEY"),
                    "replicate_token": os.getenv("REPLICATE_TOKEN"),
                    "anthropic_key": os.getenv("ANTHROPIC_API_KEY"),
                }
            },
            "agents": {
                "max_iterations": int(os.getenv("MAX_AGENT_ITERATIONS", "10")),
                "timeout": int(os.getenv("AGENT_TIMEOUT", "300")),
            }
        }
        return config
    
    async def initialize(self):
        """Initialize AI models and agents"""
        logger.info("Initializing AI Orchestrator...")
        
        # Try to detect and initialize local models
        await self._detect_local_models()
        
        # Initialize cloud models if configured
        await self._initialize_cloud_models()
        
        # Setup multi-agent framework
        await self._setup_agents()
        
        logger.info(f"AI Orchestrator initialized with {len(self.local_models)} local and {len(self.cloud_models)} cloud models")
    
    async def _detect_local_models(self):
        """Detect available local AI models"""
        try:
            # Check Ollama
            ollama_url = self.config["models"]["local"]["ollama_url"]
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{ollama_url}/api/tags", timeout=aiohttp.ClientTimeout(total=2)) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            self.local_models["ollama"] = {
                                "available": True,
                                "url": ollama_url,
                                "models": data.get("models", [])
                            }
                            logger.info(f"Ollama detected with {len(data.get('models', []))} models")
            except Exception as e:
                logger.debug(f"Ollama not available: {str(e)}")
            
            # Check for llama.cpp
            llamacpp_path = Path(self.config["models"]["local"]["llamacpp_path"])
            if llamacpp_path.exists():
                self.local_models["llamacpp"] = {
                    "available": True,
                    "path": str(llamacpp_path)
                }
                logger.info("llama.cpp detected")
            
            # Check for vLLM
            vllm_url = self.config["models"]["local"]["vllm_url"]
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{vllm_url}/health", timeout=aiohttp.ClientTimeout(total=2)) as resp:
                        if resp.status == 200:
                            self.local_models["vllm"] = {
                                "available": True,
                                "url": vllm_url
                            }
                            logger.info("vLLM detected")
            except Exception as e:
                logger.debug(f"vLLM not available: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error detecting local models: {str(e)}")
    
    async def _initialize_cloud_models(self):
        """Initialize cloud AI model connections"""
        try:
            cloud_config = self.config["models"]["cloud"]
            
            # Hugging Face
            if cloud_config.get("huggingface_token"):
                self.cloud_models["huggingface"] = {
                    "available": True,
                    "models": [
                        "meta-llama/Llama-2-70b-chat-hf",
                        "mistralai/Mixtral-8x7B-Instruct-v0.1",
                        "codellama/CodeLlama-34b-Instruct-hf",
                        "deepseek-ai/deepseek-coder-33b-instruct",
                        "WizardLM/WizardCoder-Python-34B-V1.0",
                    ]
                }
                logger.info("Hugging Face API configured")
            
            # OpenAI
            if cloud_config.get("openai_key"):
                self.cloud_models["openai"] = {
                    "available": True,
                    "models": ["gpt-4", "gpt-3.5-turbo"]
                }
                logger.info("OpenAI API configured")
            
            # Anthropic
            if cloud_config.get("anthropic_key"):
                self.cloud_models["anthropic"] = {
                    "available": True,
                    "models": ["claude-3-opus", "claude-3-sonnet"]
                }
                logger.info("Anthropic API configured")
        
        except Exception as e:
            logger.error(f"Error initializing cloud models: {str(e)}")
    
    async def _setup_agents(self):
        """Setup multi-agent framework"""
        try:
            self.agents = {
                "architect": {
                    "role": "Software Architect",
                    "goal": "Design comprehensive app architecture and tech stack",
                    "tools": ["analyze", "plan", "design"]
                },
                "coder": {
                    "role": "Senior Developer",
                    "goal": "Write clean, production-ready code",
                    "tools": ["code", "refactor", "optimize"]
                },
                "tester": {
                    "role": "QA Engineer",
                    "goal": "Test and ensure code quality",
                    "tools": ["test", "debug", "validate"]
                },
                "devops": {
                    "role": "DevOps Engineer",
                    "goal": "Setup build and deployment pipeline",
                    "tools": ["build", "deploy", "monitor"]
                },
                "ui_designer": {
                    "role": "UI/UX Designer",
                    "goal": "Design beautiful and functional interfaces",
                    "tools": ["design", "prototype", "style"]
                }
            }
            logger.info(f"Setup {len(self.agents)} specialized agents")
        except Exception as e:
            logger.error(f"Error setting up agents: {str(e)}")
    
    async def health_check(self) -> bool:
        """Check if AI services are available"""
        return len(self.local_models) > 0 or len(self.cloud_models) > 0
    
    def has_local_models(self) -> bool:
        """Check if local models are available"""
        return len(self.local_models) > 0
    
    def has_cloud_access(self) -> bool:
        """Check if cloud API access is configured"""
        return len(self.cloud_models) > 0
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List all available models"""
        models = []
        
        # Local models
        for provider, config in self.local_models.items():
            if config.get("available"):
                models.append({
                    "provider": provider,
                    "type": "local",
                    "models": config.get("models", []),
                    "status": "online"
                })
        
        # Cloud models
        for provider, config in self.cloud_models.items():
            if config.get("available"):
                models.append({
                    "provider": provider,
                    "type": "cloud",
                    "models": config.get("models", []),
                    "status": "configured"
                })
        
        return models
    
    async def create_app_plan(
        self,
        prompt: str,
        app_type: str,
        platforms: List[str],
        complexity: str = "standard",
        source_repo_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a comprehensive app plan using AI agents
        
        Args:
            prompt: User's app description
            app_type: Type of app (web, mobile, backend, full-stack)
            platforms: Target platforms
            
        Returns:
            Detailed app plan
        """
        try:
            logger.info(f"Creating app plan for: {prompt[:100]}... (complexity: {complexity})")
            
            # Apply complexity-based enhancements
            complexity_config = self._get_complexity_config(complexity)
            
            # If source repo analysis is provided, incorporate it
            base_analysis = source_repo_analysis if source_repo_analysis else {}
            
            # Use architect agent to create the plan
            plan = {
                "user_prompt": prompt,
                "app_type": app_type,
                "platforms": platforms,
                "complexity": complexity,
                "complexity_config": complexity_config,
                "source_repo": source_repo_analysis.get("repo_url") if source_repo_analysis else None,
                "architecture": await self._design_architecture(prompt, app_type, platforms, complexity),
                "tech_stack": await self._select_tech_stack(app_type, platforms, complexity),
                "features": await self._extract_features(prompt, complexity),
                "components": await self._plan_components(prompt, app_type),
                "database_schema": await self._design_database(prompt, complexity),
                "api_endpoints": await self._design_api(prompt, app_type, complexity),
                "ui_components": await self._design_ui(prompt, platforms),
                "build_config": await self._plan_build(platforms),
                "deployment_strategy": await self._plan_deployment(platforms),
                "estimated_complexity": complexity,
                "estimated_time": complexity_config["estimated_time"]
            }
            
            logger.info(f"App plan created successfully with {complexity} complexity")
            return plan
        
        except Exception as e:
            logger.error(f"Error creating app plan: {str(e)}")
            raise
    
    def _get_complexity_config(self, complexity: str) -> Dict[str, Any]:
        """Get configuration based on app complexity level"""
        configs = {
            "basic": {
                "estimated_time": "2-5 minutes",
                "features_level": "essential",
                "testing_coverage": "basic",
                "optimization_level": "minimal",
                "security_features": ["basic_auth", "input_validation"],
                "caching": False,
                "realtime_features": False,
                "advanced_db": False,
                "monitoring": False,
                "ci_cd": False
            },
            "standard": {
                "estimated_time": "5-10 minutes",
                "features_level": "complete",
                "testing_coverage": "comprehensive",
                "optimization_level": "moderate",
                "security_features": ["jwt_auth", "input_validation", "rate_limiting", "cors"],
                "caching": True,
                "realtime_features": False,
                "advanced_db": True,
                "monitoring": True,
                "ci_cd": False
            },
            "advanced": {
                "estimated_time": "10-20 minutes",
                "features_level": "enterprise",
                "testing_coverage": "complete",
                "optimization_level": "maximum",
                "security_features": ["jwt_auth", "oauth", "input_validation", "rate_limiting", 
                                     "cors", "encryption", "security_headers", "audit_logs"],
                "caching": True,
                "realtime_features": True,
                "advanced_db": True,
                "monitoring": True,
                "ci_cd": True,
                "elasticsearch": True,
                "message_queue": True,
                "microservices": True
            }
        }
        return configs.get(complexity, configs["standard"])
    
    async def _design_architecture(
        self,
        prompt: str,
        app_type: str,
        platforms: List[str],
        complexity: str = "standard"
    ) -> Dict[str, Any]:
        """Design app architecture"""
        architecture = {
            "pattern": "microservices" if "api" in prompt.lower() or "backend" in prompt.lower() else "monolithic",
            "layers": []
        }
        
        if app_type in ["full-stack", "web"]:
            architecture["layers"].extend(["frontend", "backend", "database"])
        elif app_type == "backend":
            architecture["layers"].extend(["api", "business_logic", "database"])
        elif app_type == "mobile":
            architecture["layers"].extend(["ui", "state_management", "api_client", "storage"])
        
        architecture["services"] = self._identify_services(prompt)
        architecture["data_flow"] = "client -> api -> database"
        
        return architecture
    
    def _identify_services(self, prompt: str) -> List[str]:
        """Identify required services from prompt"""
        services = ["core"]
        
        keywords = {
            "auth": ["login", "signup", "authentication", "user"],
            "payment": ["payment", "checkout", "billing", "subscription"],
            "storage": ["upload", "file", "image", "storage"],
            "notification": ["notification", "email", "sms", "alert"],
            "analytics": ["analytics", "tracking", "metrics"],
            "search": ["search", "find", "query"],
            "chat": ["chat", "messaging", "conversation"],
            "realtime": ["realtime", "live", "websocket"]
        }
        
        prompt_lower = prompt.lower()
        for service, keywords_list in keywords.items():
            if any(keyword in prompt_lower for keyword in keywords_list):
                services.append(service)
        
        return services
    
    async def _select_tech_stack(self, app_type: str, platforms: List[str], complexity: str = "standard") -> Dict[str, List[str]]:
        """Select appropriate tech stack based on complexity"""
        tech_stack = {
            "frontend": [],
            "backend": [],
            "database": [],
            "mobile": [],
            "devops": []
        }
        
        # Frontend based on complexity
        if app_type in ["full-stack", "web"] or "web" in platforms:
            if complexity == "basic":
                tech_stack["frontend"] = ["React", "TailwindCSS"]
            elif complexity == "standard":
                tech_stack["frontend"] = ["React", "Next.js", "TailwindCSS", "TypeScript"]
            else:  # advanced
                tech_stack["frontend"] = ["React", "Next.js", "TypeScript", "TailwindCSS", "Framer Motion", "React Query"]
        
        # Backend based on complexity
        if app_type in ["full-stack", "backend", "web"]:
            if complexity == "basic":
                tech_stack["backend"] = ["FastAPI", "Python"]
            elif complexity == "standard":
                tech_stack["backend"] = ["FastAPI", "Python", "Pydantic", "SQLAlchemy"]
            else:  # advanced
                tech_stack["backend"] = ["FastAPI", "Python", "Celery", "Redis", "Elasticsearch", "WebSocket"]
        
        # Database based on complexity
        if complexity == "basic":
            tech_stack["database"] = ["SQLite"]
        elif complexity == "standard":
            tech_stack["database"] = ["PostgreSQL", "Redis"]
        else:  # advanced
            tech_stack["database"] = ["PostgreSQL", "Redis", "Elasticsearch", "MongoDB"]
        
        # Mobile
        if "android" in platforms or "ios" in platforms:
            tech_stack["mobile"] = ["Capacitor", "React Native", "Expo"]
        
        # DevOps
        tech_stack["devops"] = ["Docker", "Docker Compose", "GitHub Actions"]
        
        return tech_stack
    
    async def _extract_features(self, prompt: str, complexity: str = "standard") -> List[Dict[str, str]]:
        """Extract features from user prompt based on complexity"""
        features = []
        
        # Base features for all complexity levels
        if "user" in prompt.lower() or "login" in prompt.lower():
            if complexity == "basic":
                features.append({"name": "Simple User Authentication", "priority": "high"})
            elif complexity == "standard":
                features.append({"name": "User Authentication with JWT", "priority": "high"})
            else:  # advanced
                features.append({"name": "Advanced Authentication (JWT + OAuth + 2FA)", "priority": "high"})
        
        if "dashboard" in prompt.lower():
            features.append({"name": "Dashboard", "priority": "high"})
        
        if "crud" in prompt.lower() or "manage" in prompt.lower():
            features.append({"name": "CRUD Operations", "priority": "high"})
        
        if "api" in prompt.lower():
            features.append({"name": "RESTful API", "priority": "high"})
        
        # Complexity-specific features
        if complexity == "standard" or complexity == "advanced":
            features.append({"name": "Error Handling & Logging", "priority": "high"})
            features.append({"name": "Data Validation", "priority": "medium"})
            features.append({"name": "Rate Limiting", "priority": "medium"})
        
        if complexity == "advanced":
            features.append({"name": "Real-time Updates (WebSocket)", "priority": "medium"})
            features.append({"name": "Advanced Search (Elasticsearch)", "priority": "medium"})
            features.append({"name": "Caching Layer (Redis)", "priority": "medium"})
            features.append({"name": "Background Jobs (Celery)", "priority": "medium"})
            features.append({"name": "Monitoring & Analytics", "priority": "low"})
            features.append({"name": "CI/CD Pipeline", "priority": "low"})
        
        # Add core functionality
        features.append({"name": "Core Functionality", "priority": "high"})
        
        return features
    
    async def _plan_components(self, prompt: str, app_type: str) -> List[Dict[str, Any]]:
        """Plan app components"""
        components = []
        
        if app_type in ["full-stack", "web"]:
            components.extend([
                {"name": "HomePage", "type": "page", "description": "Landing page"},
                {"name": "Dashboard", "type": "page", "description": "Main dashboard"},
                {"name": "API Routes", "type": "api", "description": "Backend endpoints"},
                {"name": "Database Models", "type": "model", "description": "Data models"}
            ])
        
        return components
    
    async def _design_database(self, prompt: str, complexity: str = "standard") -> Dict[str, Any]:
        """Design database schema based on complexity"""
        schema = {
            "tables": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "id", "type": "uuid", "primary_key": True},
                        {"name": "email", "type": "string", "unique": True},
                        {"name": "created_at", "type": "timestamp"}
                    ]
                }
            ],
            "relationships": []
        }
        
        if complexity == "standard" or complexity == "advanced":
            # Add more columns for standard/advanced
            schema["tables"][0]["columns"].extend([
                {"name": "updated_at", "type": "timestamp"},
                {"name": "last_login", "type": "timestamp"},
                {"name": "is_active", "type": "boolean"}
            ])
        
        if complexity == "advanced":
            # Add audit and advanced features
            schema["tables"][0]["columns"].extend([
                {"name": "roles", "type": "array"},
                {"name": "permissions", "type": "json"},
                {"name": "metadata", "type": "json"}
            ])
            schema["tables"].append({
                "name": "audit_logs",
                "columns": [
                    {"name": "id", "type": "uuid", "primary_key": True},
                    {"name": "user_id", "type": "uuid", "foreign_key": "users.id"},
                    {"name": "action", "type": "string"},
                    {"name": "timestamp", "type": "timestamp"},
                    {"name": "metadata", "type": "json"}
                ]
            })
        
        return schema
    
    async def _design_api(self, prompt: str, app_type: str, complexity: str = "standard") -> List[Dict[str, str]]:
        """Design API endpoints based on complexity"""
        if app_type == "frontend":
            return []
        
        endpoints = [
            {"method": "GET", "path": "/api/health", "description": "Health check"},
            {"method": "GET", "path": "/api/v1/items", "description": "List items"},
            {"method": "POST", "path": "/api/v1/items", "description": "Create item"},
            {"method": "GET", "path": "/api/v1/items/{id}", "description": "Get item"},
            {"method": "PUT", "path": "/api/v1/items/{id}", "description": "Update item"},
            {"method": "DELETE", "path": "/api/v1/items/{id}", "description": "Delete item"}
        ]
        
        if complexity == "standard" or complexity == "advanced":
            endpoints.extend([
                {"method": "GET", "path": "/api/v1/items/search", "description": "Search items"},
                {"method": "POST", "path": "/api/v1/items/bulk", "description": "Bulk create"},
                {"method": "GET", "path": "/api/v1/stats", "description": "Get statistics"}
            ])
        
        if complexity == "advanced":
            endpoints.extend([
                {"method": "GET", "path": "/api/v1/analytics", "description": "Analytics data"},
                {"method": "WS", "path": "/ws/realtime", "description": "WebSocket real-time updates"},
                {"method": "GET", "path": "/api/v1/export", "description": "Export data"},
                {"method": "POST", "path": "/api/v1/import", "description": "Import data"}
            ])
        
        return endpoints
    
    async def _design_ui(self, prompt: str, platforms: List[str]) -> List[Dict[str, str]]:
        """Design UI components"""
        ui_components = [
            {"name": "Header", "type": "navigation"},
            {"name": "Footer", "type": "navigation"},
            {"name": "Sidebar", "type": "navigation"},
            {"name": "Card", "type": "display"},
            {"name": "Form", "type": "input"},
            {"name": "Button", "type": "action"},
            {"name": "Modal", "type": "overlay"}
        ]
        return ui_components
    
    async def _plan_build(self, platforms: List[str]) -> Dict[str, Any]:
        """Plan build configuration"""
        build_config = {
            "platforms": platforms,
            "tools": {}
        }
        
        if "web" in platforms:
            build_config["tools"]["web"] = {
                "bundler": "vite",
                "target": "es2020",
                "output": "dist/"
            }
        
        if "android" in platforms:
            build_config["tools"]["android"] = {
                "builder": "capacitor",
                "sdk_version": "33",
                "output": "android/app/build/outputs/"
            }
        
        if "ios" in platforms:
            build_config["tools"]["ios"] = {
                "builder": "capacitor",
                "deployment_target": "13.0",
                "output": "ios/App/build/"
            }
        
        return build_config
    
    async def _plan_deployment(self, platforms: List[str]) -> Dict[str, Any]:
        """Plan deployment strategy"""
        deployment = {
            "strategy": "containerized",
            "targets": []
        }
        
        if "web" in platforms:
            deployment["targets"].append({
                "platform": "web",
                "method": "docker",
                "hosting": ["vercel", "netlify", "cloudflare-pages"]
            })
        
        if "android" in platforms:
            deployment["targets"].append({
                "platform": "android",
                "method": "apk",
                "distribution": ["direct-download", "play-store"]
            })
        
        return deployment
    
    async def process_voice_command(self, text: str) -> Dict[str, Any]:
        """
        Process voice command and generate response
        
        Args:
            text: Transcribed voice command
            
        Returns:
            Response with text and action
        """
        try:
            logger.info(f"Processing voice command: {text}")
            
            # Parse command intent
            intent = self._parse_intent(text)
            
            # Generate response based on intent
            if intent == "create_app":
                response_text = "I'll help you create an app. What kind of app would you like to make?"
                action = "prompt_app_details"
            elif intent == "analyze_repo":
                response_text = "Please provide the GitHub repository URL you'd like me to analyze."
                action = "prompt_repo_url"
            elif intent == "build_app":
                response_text = "Which platforms would you like to build for? Android, iOS, Web, or Desktop?"
                action = "prompt_platforms"
            elif intent == "help":
                response_text = "I can help you create apps, analyze GitHub repositories, build for multiple platforms, and more. Just tell me what you need!"
                action = "show_help"
            else:
                response_text = "I'm not sure I understood that. Could you rephrase your request?"
                action = "clarify"
            
            return {
                "text": response_text,
                "intent": intent,
                "action": action
            }
        
        except Exception as e:
            logger.error(f"Error processing voice command: {str(e)}")
            return {
                "text": "Sorry, I encountered an error processing your command.",
                "intent": "error",
                "action": "none"
            }
    
    def _parse_intent(self, text: str) -> str:
        """Parse user intent from text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["create", "make", "build", "generate"]):
            return "create_app"
        elif any(word in text_lower for word in ["analyze", "check", "look at", "examine"]):
            return "analyze_repo"
        elif "build" in text_lower and any(word in text_lower for word in ["android", "ios", "mobile"]):
            return "build_app"
        elif any(word in text_lower for word in ["help", "what can you do", "how do"]):
            return "help"
        else:
            return "unknown"
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up AI Orchestrator...")
        # Close any open connections, cleanup resources
        pass
