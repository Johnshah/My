"""
Build Service
Handles building apps for different platforms:
- Web (Vite/Next.js/Static)
- Android (Capacitor/React Native)
- iOS (Capacitor/React Native)
- Desktop (Electron)
"""

import os
import logging
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class BuildService:
    """Service for building apps across multiple platforms"""
    
    def __init__(self):
        self.build_cache_dir = Path("/tmp/my_builds")
        self.build_cache_dir.mkdir(exist_ok=True, parents=True)
    
    async def build_web(self, project_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Build web application"""
        logger.info(f"Building web app from {project_path}")
        
        try:
            project_path = Path(project_path)
            frontend_path = project_path / "frontend"
            
            if not frontend_path.exists():
                frontend_path = project_path
            
            # Check for package.json
            if (frontend_path / "package.json").exists():
                # Install dependencies
                logger.info("Installing dependencies...")
                proc = await asyncio.create_subprocess_exec(
                    "npm", "install",
                    cwd=str(frontend_path),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await proc.communicate()
                
                # Build
                logger.info("Building for production...")
                proc = await asyncio.create_subprocess_exec(
                    "npm", "run", "build",
                    cwd=str(frontend_path),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await proc.communicate()
                
                if proc.returncode == 0:
                    return {
                        "status": "success",
                        "platform": "web",
                        "output": str(frontend_path / "dist"),
                        "message": "Web build completed successfully"
                    }
                else:
                    return {
                        "status": "error",
                        "platform": "web",
                        "error": stderr.decode() if stderr else "Build failed"
                    }
            else:
                return {
                    "status": "error",
                    "platform": "web",
                    "error": "No package.json found"
                }
        
        except Exception as e:
            logger.error(f"Web build error: {str(e)}")
            return {
                "status": "error",
                "platform": "web",
                "error": str(e)
            }
    
    async def build_android(self, project_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Build Android APK"""
        logger.info(f"Building Android app from {project_path}")
        
        try:
            project_path = Path(project_path)
            
            # Check for Capacitor
            capacitor_config = project_path / "capacitor.config.json"
            if capacitor_config.exists():
                return await self._build_capacitor_android(project_path, options)
            
            # Check for React Native
            android_dir = project_path / "android"
            if android_dir.exists():
                return await self._build_react_native_android(project_path, options)
            
            # No mobile setup found, need to initialize
            return {
                "status": "pending_setup",
                "platform": "android",
                "message": "Android build requires Capacitor or React Native setup",
                "next_steps": [
                    "Initialize Capacitor: npx cap init",
                    "Add Android platform: npx cap add android",
                    "Or use React Native: npx react-native init"
                ]
            }
        
        except Exception as e:
            logger.error(f"Android build error: {str(e)}")
            return {
                "status": "error",
                "platform": "android",
                "error": str(e)
            }
    
    async def _build_capacitor_android(self, project_path: Path, options: Dict[str, Any]) -> Dict[str, Any]:
        """Build using Capacitor"""
        try:
            # Sync web assets
            proc = await asyncio.create_subprocess_exec(
                "npx", "cap", "sync", "android",
                cwd=str(project_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            
            # Build APK
            android_path = project_path / "android"
            proc = await asyncio.create_subprocess_exec(
                "./gradlew", "assembleDebug",
                cwd=str(android_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                apk_path = android_path / "app/build/outputs/apk/debug/app-debug.apk"
                return {
                    "status": "success",
                    "platform": "android",
                    "output": str(apk_path),
                    "message": "Android APK built successfully",
                    "apk_size": os.path.getsize(apk_path) if apk_path.exists() else 0
                }
            else:
                return {
                    "status": "error",
                    "platform": "android",
                    "error": stderr.decode() if stderr else "Build failed"
                }
        
        except Exception as e:
            logger.error(f"Capacitor Android build error: {str(e)}")
            return {"status": "error", "platform": "android", "error": str(e)}
    
    async def _build_react_native_android(self, project_path: Path, options: Dict[str, Any]) -> Dict[str, Any]:
        """Build using React Native"""
        try:
            # Build APK
            proc = await asyncio.create_subprocess_exec(
                "npx", "react-native", "build-android", "--mode=release",
                cwd=str(project_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                apk_path = project_path / "android/app/build/outputs/apk/release/app-release.apk"
                return {
                    "status": "success",
                    "platform": "android",
                    "output": str(apk_path),
                    "message": "React Native Android APK built successfully"
                }
            else:
                return {
                    "status": "error",
                    "platform": "android",
                    "error": stderr.decode() if stderr else "Build failed"
                }
        
        except Exception as e:
            logger.error(f"React Native Android build error: {str(e)}")
            return {"status": "error", "platform": "android", "error": str(e)}
    
    async def build_ios(self, project_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Build iOS app (requires macOS)"""
        logger.info(f"Building iOS app from {project_path}")
        
        # Check if running on macOS
        if os.uname().sysname != "Darwin":
            return {
                "status": "unsupported",
                "platform": "ios",
                "message": "iOS builds require macOS with Xcode installed",
                "alternatives": [
                    "Use a macOS machine",
                    "Use cloud build service (e.g., Expo EAS)",
                    "Use CI/CD with macOS runner (GitHub Actions)"
                ]
            }
        
        try:
            project_path = Path(project_path)
            
            # Check for Capacitor
            capacitor_config = project_path / "capacitor.config.json"
            if capacitor_config.exists():
                # Sync
                proc = await asyncio.create_subprocess_exec(
                    "npx", "cap", "sync", "ios",
                    cwd=str(project_path),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await proc.communicate()
                
                return {
                    "status": "ready_for_xcode",
                    "platform": "ios",
                    "message": "iOS project synced. Open in Xcode to build",
                    "xcode_project": str(project_path / "ios/App/App.xcworkspace")
                }
            
            return {
                "status": "pending_setup",
                "platform": "ios",
                "message": "iOS build requires Capacitor setup"
            }
        
        except Exception as e:
            logger.error(f"iOS build error: {str(e)}")
            return {"status": "error", "platform": "ios", "error": str(e)}
    
    async def build_desktop(self, project_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Build desktop app using Electron"""
        logger.info(f"Building desktop app from {project_path}")
        
        try:
            project_path = Path(project_path)
            
            # Check for Electron
            package_json = project_path / "package.json"
            if package_json.exists():
                with open(package_json, 'r') as f:
                    package_data = json.load(f)
                    
                if "electron" in package_data.get("dependencies", {}) or \
                   "electron" in package_data.get("devDependencies", {}):
                    # Build with Electron
                    proc = await asyncio.create_subprocess_exec(
                        "npm", "run", "build",
                        cwd=str(project_path),
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    await proc.communicate()
                    
                    proc = await asyncio.create_subprocess_exec(
                        "npm", "run", "package",
                        cwd=str(project_path),
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, stderr = await proc.communicate()
                    
                    if proc.returncode == 0:
                        return {
                            "status": "success",
                            "platform": "desktop",
                            "output": str(project_path / "dist"),
                            "message": "Desktop app built successfully"
                        }
            
            return {
                "status": "pending_setup",
                "platform": "desktop",
                "message": "Desktop build requires Electron setup",
                "next_steps": [
                    "Install Electron: npm install electron --save-dev",
                    "Add electron-builder: npm install electron-builder --save-dev",
                    "Configure package.json with build scripts"
                ]
            }
        
        except Exception as e:
            logger.error(f"Desktop build error: {str(e)}")
            return {"status": "error", "platform": "desktop", "error": str(e)}
