"""
My - Universal AI App Generator
FastAPI Backend Main Entry Point

This is the core backend server that orchestrates:
- GitHub repo analysis
- AI model coordination
- Code generation
- Multi-platform builds
- Voice assistant integration
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
import os
import json
import asyncio
from datetime import datetime
import logging

# Import our custom modules
from services.github_service import GitHubService
from services.ai_orchestrator import AIOrchestrator
from services.code_generator import CodeGenerator
from services.build_service import BuildService
from services.voice_service import VoiceService
from services.deep_mode import DeepMode
from database.db import Database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="My - Universal AI App Generator",
    description="Free, open-source AI platform for generating real, working apps",
    version="1.0.0"
)

# CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
db = Database()
github_service = GitHubService()
ai_orchestrator = AIOrchestrator()
code_generator = CodeGenerator()
build_service = BuildService()
voice_service = VoiceService()
deep_mode = DeepMode()

# Pydantic models for request/response
class GitHubRepoRequest(BaseModel):
    repo_url: HttpUrl
    branch: Optional[str] = "main"
    include_analysis: bool = True

class TextPromptRequest(BaseModel):
    prompt: str
    app_type: Optional[str] = "full-stack"  # web, mobile, backend, full-stack
    platform: Optional[List[str]] = ["web"]  # web, android, ios, desktop

class ProjectAnalysisResponse(BaseModel):
    project_id: str
    status: str
    analysis: Optional[Dict[str, Any]] = None
    tech_stack: Optional[List[str]] = None
    dependencies: Optional[Dict[str, List[str]]] = None
    structure: Optional[Dict[str, Any]] = None

class BuildRequest(BaseModel):
    project_id: str
    platforms: List[str]  # web, android, ios, desktop
    build_options: Optional[Dict[str, Any]] = {}

class VoiceCommandRequest(BaseModel):
    audio_data: Optional[str] = None  # base64 encoded audio
    text: Optional[str] = None  # or direct text command

# Root endpoint
@app.get("/")
async def root():
    return {
        "app": "My - Universal AI App Generator",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "analyze_github": "/api/v1/analyze/github",
            "analyze_upload": "/api/v1/analyze/upload",
            "generate_from_prompt": "/api/v1/generate/prompt",
            "build_app": "/api/v1/build",
            "voice_command": "/api/v1/voice/command",
            "list_models": "/api/v1/models/list",
            "projects": "/api/v1/projects"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": await db.health_check(),
            "ai_models": await ai_orchestrator.health_check(),
            "github": github_service.is_configured(),
            "voice": voice_service.is_available()
        }
    }

@app.post("/api/v1/analyze/github", response_model=ProjectAnalysisResponse)
async def analyze_github_repo(request: GitHubRepoRequest, background_tasks: BackgroundTasks):
    """
    Analyze a GitHub repository and prepare for app generation
    
    This endpoint:
    1. Clones the repo
    2. Analyzes the code structure
    3. Detects tech stack and dependencies
    4. Prepares AI models for code generation
    """
    try:
        logger.info(f"Analyzing GitHub repo: {request.repo_url}")
        
        # Create project entry
        project_id = await db.create_project({
            "source": "github",
            "repo_url": str(request.repo_url),
            "branch": request.branch,
            "status": "analyzing"
        })
        
        # Start analysis in background
        background_tasks.add_task(
            _analyze_github_background,
            project_id,
            str(request.repo_url),
            request.branch,
            request.include_analysis
        )
        
        return ProjectAnalysisResponse(
            project_id=project_id,
            status="analyzing",
            analysis=None
        )
    
    except Exception as e:
        logger.error(f"Error analyzing GitHub repo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def _analyze_github_background(project_id: str, repo_url: str, branch: str, include_analysis: bool):
    """Background task for GitHub repo analysis"""
    try:
        # Clone repository
        repo_path = await github_service.clone_repo(repo_url, branch)
        
        # Analyze code structure
        analysis = await github_service.analyze_repo(repo_path)
        
        # Detect tech stack
        tech_stack = await github_service.detect_tech_stack(repo_path)
        
        # Get dependencies
        dependencies = await github_service.extract_dependencies(repo_path)
        
        # Update project with analysis results
        await db.update_project(project_id, {
            "status": "analyzed",
            "repo_path": repo_path,
            "analysis": analysis,
            "tech_stack": tech_stack,
            "dependencies": dependencies,
            "analyzed_at": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Analysis complete for project {project_id}")
        
    except Exception as e:
        logger.error(f"Background analysis failed: {str(e)}")
        await db.update_project(project_id, {
            "status": "error",
            "error": str(e)
        })

@app.post("/api/v1/analyze/upload")
async def analyze_uploaded_project(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Analyze an uploaded project file (ZIP or folder)
    """
    try:
        logger.info(f"Analyzing uploaded file: {file.filename}")
        
        # Save uploaded file
        upload_path = f"/tmp/my_uploads/{datetime.utcnow().timestamp()}_{file.filename}"
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        
        with open(upload_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Create project entry
        project_id = await db.create_project({
            "source": "upload",
            "filename": file.filename,
            "upload_path": upload_path,
            "status": "analyzing"
        })
        
        # Extract and analyze
        background_tasks.add_task(
            _analyze_upload_background,
            project_id,
            upload_path
        )
        
        return {
            "project_id": project_id,
            "status": "analyzing",
            "filename": file.filename
        }
    
    except Exception as e:
        logger.error(f"Error analyzing upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def _analyze_upload_background(project_id: str, upload_path: str):
    """Background task for uploaded file analysis"""
    try:
        # Extract if ZIP
        extracted_path = await github_service.extract_archive(upload_path)
        
        # Analyze
        analysis = await github_service.analyze_repo(extracted_path)
        tech_stack = await github_service.detect_tech_stack(extracted_path)
        dependencies = await github_service.extract_dependencies(extracted_path)
        
        # Update project
        await db.update_project(project_id, {
            "status": "analyzed",
            "repo_path": extracted_path,
            "analysis": analysis,
            "tech_stack": tech_stack,
            "dependencies": dependencies,
            "analyzed_at": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Upload analysis failed: {str(e)}")
        await db.update_project(project_id, {"status": "error", "error": str(e)})

@app.post("/api/v1/generate/prompt")
async def generate_from_prompt(request: TextPromptRequest, background_tasks: BackgroundTasks):
    """
    Generate a complete app from a text prompt
    
    This is the most powerful feature - creates apps from scratch!
    """
    try:
        logger.info(f"Generating app from prompt: {request.prompt[:100]}...")
        
        # Create project
        project_id = await db.create_project({
            "source": "prompt",
            "prompt": request.prompt,
            "app_type": request.app_type,
            "platforms": request.platform,
            "status": "generating"
        })
        
        # Start generation in background
        background_tasks.add_task(
            _generate_from_prompt_background,
            project_id,
            request.prompt,
            request.app_type,
            request.platform
        )
        
        return {
            "project_id": project_id,
            "status": "generating",
            "message": "AI is creating your app... This may take a few minutes."
        }
    
    except Exception as e:
        logger.error(f"Error generating from prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def _generate_from_prompt_background(
    project_id: str,
    prompt: str,
    app_type: str,
    platforms: List[str]
):
    """Background task for prompt-based app generation"""
    try:
        # Use AI orchestrator to plan the app
        plan = await ai_orchestrator.create_app_plan(prompt, app_type, platforms)
        
        await db.update_project(project_id, {
            "status": "planned",
            "plan": plan
        })
        
        # Generate code using multiple AI models
        generated_code = await code_generator.generate_full_app(plan)
        
        await db.update_project(project_id, {
            "status": "generated",
            "code": generated_code
        })
        
        # Create project structure
        project_path = await code_generator.create_project_structure(
            project_id,
            generated_code
        )
        
        await db.update_project(project_id, {
            "status": "ready",
            "repo_path": project_path,
            "generated_at": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Generation complete for project {project_id}")
        
    except Exception as e:
        logger.error(f"Generation failed: {str(e)}")
        await db.update_project(project_id, {"status": "error", "error": str(e)})

@app.post("/api/v1/generate/deep-mode")
async def generate_deep_mode(request: TextPromptRequest, background_tasks: BackgroundTasks):
    """
    🚀 DEEP MODE - Ultra Advanced App Generation
    
    This mode creates production-ready apps with extreme precision:
    - Generates each file individually with validation
    - Advanced error checking and correction
    - Comprehensive testing for each component
    - Optimization passes
    - Security audits
    - Takes more time but produces error-free applications
    
    Perfect for:
    - Production applications
    - Complex projects
    - When quality is critical
    - Professional deployments
    """
    try:
        logger.info(f"🚀 Starting Deep Mode generation: {request.prompt[:100]}...")
        
        # Create project
        project_id = await db.create_project({
            "source": "prompt_deep",
            "prompt": request.prompt,
            "app_type": request.app_type,
            "platforms": request.platform,
            "mode": "deep",
            "status": "initializing"
        })
        
        # Start Deep Mode generation
        background_tasks.add_task(
            _generate_deep_mode_background,
            project_id,
            request.prompt,
            request.app_type,
            request.platform
        )
        
        return {
            "project_id": project_id,
            "mode": "deep",
            "status": "initializing",
            "message": "🚀 Deep Mode activated! AI is creating your production-ready app with extreme precision. This will take 10-20 minutes for maximum quality.",
            "estimated_time": "10-20 minutes",
            "features": [
                "File-by-file generation with validation",
                "Advanced error checking",
                "Comprehensive testing",
                "Performance optimization",
                "Security audits",
                "Complete documentation"
            ]
        }
    
    except Exception as e:
        logger.error(f"Error starting Deep Mode: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def _generate_deep_mode_background(
    project_id: str,
    prompt: str,
    app_type: str,
    platforms: List[str]
):
    """Background task for Deep Mode generation"""
    try:
        # Progress callback
        async def update_progress(progress_data: Dict[str, Any]):
            await db.update_project(project_id, {
                "progress": progress_data["progress"],
                "progress_message": progress_data["message"],
                "stats": progress_data["stats"]
            })
        
        # Create plan
        plan = await ai_orchestrator.create_app_plan(prompt, app_type, platforms)
        
        await db.update_project(project_id, {
            "status": "planning_complete",
            "plan": plan
        })
        
        # Generate with Deep Mode
        result = await deep_mode.generate_app_deep_mode(
            plan,
            project_id,
            progress_callback=update_progress
        )
        
        # Save results
        await db.update_project(project_id, {
            "status": "completed",
            "project": result["project"],
            "stats": result["stats"],
            "quality_score": result["quality_score"],
            "time_taken": result["time_taken"],
            "completed_at": datetime.utcnow().isoformat()
        })
        
        logger.info(f"✅ Deep Mode completed for project {project_id}")
        logger.info(f"Quality Score: {result['quality_score']:.2f}/100")
        
    except Exception as e:
        logger.error(f"Deep Mode failed: {str(e)}")
        await db.update_project(project_id, {
            "status": "error",
            "error": str(e)
        })

@app.post("/api/v1/build")
async def build_app(request: BuildRequest, background_tasks: BackgroundTasks):
    """
    Build app for specified platforms (Android, iOS, Web, Desktop)
    """
    try:
        # Get project
        project = await db.get_project(request.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Start build process
        build_id = await db.create_build({
            "project_id": request.project_id,
            "platforms": request.platforms,
            "options": request.build_options,
            "status": "building"
        })
        
        background_tasks.add_task(
            _build_app_background,
            build_id,
            request.project_id,
            request.platforms,
            request.build_options
        )
        
        return {
            "build_id": build_id,
            "status": "building",
            "platforms": request.platforms
        }
    
    except Exception as e:
        logger.error(f"Error starting build: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def _build_app_background(
    build_id: str,
    project_id: str,
    platforms: List[str],
    options: Dict[str, Any]
):
    """Background task for app building"""
    try:
        project = await db.get_project(project_id)
        
        build_results = {}
        for platform in platforms:
            logger.info(f"Building for platform: {platform}")
            
            if platform == "web":
                result = await build_service.build_web(project["repo_path"], options)
            elif platform == "android":
                result = await build_service.build_android(project["repo_path"], options)
            elif platform == "ios":
                result = await build_service.build_ios(project["repo_path"], options)
            elif platform == "desktop":
                result = await build_service.build_desktop(project["repo_path"], options)
            else:
                result = {"status": "unsupported", "platform": platform}
            
            build_results[platform] = result
        
        await db.update_build(build_id, {
            "status": "completed",
            "results": build_results,
            "completed_at": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Build failed: {str(e)}")
        await db.update_build(build_id, {"status": "error", "error": str(e)})

@app.post("/api/v1/voice/command")
async def process_voice_command(request: VoiceCommandRequest):
    """
    Process voice commands using Whisper + AI
    """
    try:
        # Transcribe audio if provided
        if request.audio_data:
            text = await voice_service.transcribe(request.audio_data)
        else:
            text = request.text
        
        if not text:
            raise HTTPException(status_code=400, detail="No text or audio provided")
        
        # Process command
        response = await ai_orchestrator.process_voice_command(text)
        
        # Generate voice response
        audio_response = await voice_service.synthesize(response["text"])
        
        return {
            "transcribed_text": text,
            "response": response,
            "audio": audio_response
        }
    
    except Exception as e:
        logger.error(f"Voice command error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/models/list")
async def list_available_models():
    """
    List all available AI models (local and cloud)
    """
    try:
        models = await ai_orchestrator.list_models()
        return {
            "models": models,
            "count": len(models),
            "local_available": ai_orchestrator.has_local_models(),
            "cloud_configured": ai_orchestrator.has_cloud_access()
        }
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/projects")
async def list_projects(skip: int = 0, limit: int = 20):
    """
    List all projects
    """
    try:
        projects = await db.list_projects(skip, limit)
        return {
            "projects": projects,
            "count": len(projects)
        }
    except Exception as e:
        logger.error(f"Error listing projects: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/projects/{project_id}")
async def get_project(project_id: str):
    """
    Get project details
    """
    try:
        project = await db.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/projects/{project_id}")
async def delete_project(project_id: str):
    """
    Delete a project
    """
    try:
        await db.delete_project(project_id)
        return {"status": "deleted", "project_id": project_id}
    except Exception as e:
        logger.error(f"Error deleting project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 Starting My - Universal AI App Generator")
    await db.initialize()
    await ai_orchestrator.initialize()
    logger.info("✅ All services initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 Shutting down My - Universal AI App Generator")
    await db.close()
    await ai_orchestrator.cleanup()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
