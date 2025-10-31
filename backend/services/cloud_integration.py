"""
Cloud Integration Service - GenSpark-style Cloud Processing
Integrates with Hugging Face Inference API, Replicate, and other cloud AI services
All heavy processing happens in the cloud for free/unlimited generation
"""

import os
import asyncio
from typing import Dict, Any, Optional, List
import logging
import aiohttp

logger = logging.getLogger(__name__)


class CloudIntegrationService:
    """Manages cloud AI service integration for unlimited free processing"""
    
    def __init__(self):
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY", "")
        self.replicate_api_key = os.getenv("REPLICATE_API_TOKEN", "")
        self.hf_api_url = "https://api-inference.huggingface.co/models"
        self.replicate_api_url = "https://api.replicate.com/v1/predictions"
    
    async def generate_code_cloud(
        self,
        prompt: str,
        model: str = "bigcode/starcoder",
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> str:
        """Generate code using cloud AI services"""
        
        # Try Hugging Face first (free tier available)
        if self.hf_api_key:
            try:
                return await self._generate_hf(prompt, model, max_tokens, temperature)
            except Exception as e:
                logger.warning(f"HF generation failed: {e}")
        
        # Try Replicate (pay-as-you-go, but user can provide token)
        if self.replicate_api_key:
            try:
                return await self._generate_replicate(prompt, model, max_tokens, temperature)
            except Exception as e:
                logger.warning(f"Replicate generation failed: {e}")
        
        # Fallback to template
        return self._generate_template_code(prompt)
    
    async def _generate_hf(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate using Hugging Face Inference API"""
        url = f"{self.hf_api_url}/{model}"
        headers = {"Authorization": f"Bearer {self.hf_api_key}"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "return_full_text": False
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=120) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if isinstance(result, list) and len(result) > 0:
                        return result[0].get("generated_text", "")
                    return ""
                else:
                    error = await resp.text()
                    raise Exception(f"HF API error: {error}")
    
    async def _generate_replicate(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate using Replicate API"""
        headers = {
            "Authorization": f"Token {self.replicate_api_key}",
            "Content-Type": "application/json"
        }
        
        # Map to Replicate model format
        replicate_model = "meta/codellama-70b-instruct"
        
        payload = {
            "version": "latest",
            "input": {
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
        }
        
        async with aiohttp.ClientSession() as session:
            # Create prediction
            async with session.post(
                self.replicate_api_url,
                headers=headers,
                json={"version": replicate_model, **payload},
                timeout=30
            ) as resp:
                if resp.status == 201:
                    prediction = await resp.json()
                    prediction_id = prediction["id"]
                    
                    # Poll for result
                    for _ in range(60):  # Poll for up to 2 minutes
                        await asyncio.sleep(2)
                        
                        async with session.get(
                            f"{self.replicate_api_url}/{prediction_id}",
                            headers=headers
                        ) as check_resp:
                            if check_resp.status == 200:
                                result = await check_resp.json()
                                status = result.get("status")
                                
                                if status == "succeeded":
                                    output = result.get("output", [])
                                    return "".join(output) if isinstance(output, list) else str(output)
                                elif status == "failed":
                                    raise Exception(f"Replicate prediction failed: {result.get('error')}")
                    
                    raise Exception("Replicate prediction timeout")
                else:
                    error = await resp.text()
                    raise Exception(f"Replicate API error: {error}")
    
    def _generate_template_code(self, prompt: str) -> str:
        """Fallback template code generation"""
        return f"""# Generated code for: {prompt}

def main():
    \"\"\"Main application entry point\"\"\"
    print("Hello from Universal AI App Generator!")
    print("This is a template. Install AI models for real code generation.")

if __name__ == "__main__":
    main()
"""
    
    async def generate_image_cloud(
        self,
        prompt: str,
        model: str = "stabilityai/stable-diffusion-xl-base-1.0",
        width: int = 1024,
        height: int = 1024
    ) -> bytes:
        """Generate image using cloud services"""
        
        if self.hf_api_key:
            try:
                return await self._generate_image_hf(prompt, model, width, height)
            except Exception as e:
                logger.error(f"HF image generation failed: {e}")
        
        if self.replicate_api_key:
            try:
                return await self._generate_image_replicate(prompt, width, height)
            except Exception as e:
                logger.error(f"Replicate image generation failed: {e}")
        
        return b""
    
    async def _generate_image_hf(
        self,
        prompt: str,
        model: str,
        width: int,
        height: int
    ) -> bytes:
        """Generate image using Hugging Face"""
        url = f"{self.hf_api_url}/{model}"
        headers = {"Authorization": f"Bearer {self.hf_api_key}"}
        payload = {
            "inputs": prompt,
            "parameters": {"width": width, "height": height}
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=180) as resp:
                if resp.status == 200:
                    return await resp.read()
                else:
                    raise Exception(f"HF image generation failed: {await resp.text()}")
    
    async def _generate_image_replicate(
        self,
        prompt: str,
        width: int,
        height: int
    ) -> bytes:
        """Generate image using Replicate"""
        # Similar to code generation but for SDXL
        # Implementation similar to _generate_replicate
        pass
    
    async def transcribe_audio_cloud(
        self,
        audio_file: str,
        model: str = "openai/whisper-large-v3"
    ) -> Dict[str, Any]:
        """Transcribe audio using cloud services"""
        
        if self.hf_api_key:
            try:
                return await self._transcribe_hf(audio_file, model)
            except Exception as e:
                logger.error(f"HF transcription failed: {e}")
        
        return {"text": "", "error": "No cloud API keys configured"}
    
    async def _transcribe_hf(self, audio_file: str, model: str) -> Dict[str, Any]:
        """Transcribe audio using Hugging Face"""
        url = f"{self.hf_api_url}/{model}"
        headers = {"Authorization": f"Bearer {self.hf_api_key}"}
        
        with open(audio_file, "rb") as f:
            audio_data = f.read()
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=audio_data, timeout=180) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return {"text": result.get("text", ""), "confidence": 1.0}
                else:
                    raise Exception(f"HF transcription failed: {await resp.text()}")
    
    def get_cloud_status(self) -> Dict[str, Any]:
        """Get cloud service availability status"""
        return {
            "huggingface": {
                "available": bool(self.hf_api_key),
                "services": ["code_generation", "image_generation", "audio_transcription"]
            },
            "replicate": {
                "available": bool(self.replicate_api_key),
                "services": ["code_generation", "image_generation"]
            },
            "processing_mode": "cloud" if (self.hf_api_key or self.replicate_api_key) else "local"
        }


# Singleton instance
cloud_service = CloudIntegrationService()
