"""
Real AI Model Manager
Manages local and cloud AI models with actual integration
Supports: Ollama, Transformers, Hugging Face, Replicate
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union
import asyncio
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class ModelManager:
    """
    Complete AI Model Manager with real integration
    Supports both offline (Ollama, Transformers) and online (HF, Replicate) models
    """
    
    def __init__(self):
        self.models = {}
        self.ollama_available = False
        self.transformers_available = False
        self.hf_available = False
        self.replicate_available = False
        
        # API keys from environment
        self.hf_token = os.getenv("HUGGINGFACE_TOKEN")
        self.replicate_token = os.getenv("REPLICATE_TOKEN")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize available model backends"""
        
        # Check Ollama
        try:
            import ollama
            self.ollama_available = True
            logger.info("✅ Ollama available for local models")
        except ImportError:
            logger.info("ℹ️ Ollama not installed (optional)")
        
        # Check Transformers
        try:
            import transformers
            import torch
            self.transformers_available = True
            logger.info(f"✅ Transformers available (CUDA: {torch.cuda.is_available()})")
        except ImportError:
            logger.info("ℹ️ Transformers not installed (optional)")
        
        # Check Hugging Face
        if self.hf_token:
            self.hf_available = True
            logger.info("✅ Hugging Face API configured")
        
        # Check Replicate
        if self.replicate_token:
            self.replicate_available = True
            logger.info("✅ Replicate API configured")
    
    async def generate_code(
        self,
        prompt: str,
        language: str = "python",
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> str:
        """
        Generate code using available models
        Priority: Ollama > Transformers > Hugging Face > Replicate
        """
        
        # Try Ollama first (fastest for local)
        if self.ollama_available:
            try:
                return await self._generate_with_ollama(prompt, max_tokens, temperature)
            except Exception as e:
                logger.warning(f"Ollama failed: {e}, trying next option...")
        
        # Try Transformers (local but slower)
        if self.transformers_available:
            try:
                return await self._generate_with_transformers(prompt, max_tokens, temperature)
            except Exception as e:
                logger.warning(f"Transformers failed: {e}, trying next option...")
        
        # Try Hugging Face API (cloud)
        if self.hf_available:
            try:
                return await self._generate_with_huggingface(prompt, max_tokens, temperature)
            except Exception as e:
                logger.warning(f"Hugging Face failed: {e}, trying next option...")
        
        # Try Replicate API (cloud)
        if self.replicate_available:
            try:
                return await self._generate_with_replicate(prompt, max_tokens, temperature)
            except Exception as e:
                logger.error(f"All generation methods failed. Last error: {e}")
        
        # Fallback: Template-based generation
        logger.warning("⚠️ No AI models available, using template-based generation")
        return self._generate_template_code(prompt, language)
    
    async def _generate_with_ollama(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate using Ollama (local)"""
        import ollama
        
        # Use CodeLlama or DeepSeek Coder
        model = "deepseek-coder:6.7b"  # or "codellama:7b"
        
        response = await asyncio.to_thread(
            ollama.generate,
            model=model,
            prompt=prompt,
            options={
                "num_predict": max_tokens,
                "temperature": temperature
            }
        )
        
        return response['response']
    
    async def _generate_with_transformers(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate using Transformers (local)"""
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch
        
        # Use CodeLlama or similar
        model_name = "codellama/CodeLlama-7b-Instruct-hf"
        
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto"
        )
        
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        outputs = await asyncio.to_thread(
            model.generate,
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=True
        )
        
        generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated[len(prompt):]  # Return only new generated text
    
    async def _generate_with_huggingface(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate using Hugging Face Inference API"""
        from huggingface_hub import InferenceClient
        
        client = InferenceClient(token=self.hf_token)
        
        # Use DeepSeek Coder or CodeLlama via Inference API
        response = await asyncio.to_thread(
            client.text_generation,
            prompt,
            model="deepseek-ai/deepseek-coder-6.7b-instruct",
            max_new_tokens=max_tokens,
            temperature=temperature
        )
        
        return response
    
    async def _generate_with_replicate(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate using Replicate API"""
        import replicate
        
        output = await asyncio.to_thread(
            replicate.run,
            "meta/codellama-7b-instruct:latest",
            input={
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
        )
        
        return "".join(output)
    
    def _generate_template_code(self, prompt: str, language: str) -> str:
        """Fallback: Template-based code generation"""
        
        templates = {
            "python": '''"""
{description}
"""

def main():
    # TODO: Implement functionality
    print("Generated by My AI App Generator")
    pass

if __name__ == "__main__":
    main()
''',
            "javascript": '''/**
 * {description}
 */

function main() {{
    // TODO: Implement functionality
    console.log("Generated by My AI App Generator");
}}

main();
''',
            "typescript": '''/**
 * {description}
 */

function main(): void {{
    // TODO: Implement functionality
    console.log("Generated by My AI App Generator");
}}

main();
'''
        }
        
        template = templates.get(language, templates["python"])
        return template.format(description=prompt[:200])
    
    async def analyze_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Analyze code quality and complexity"""
        analysis = {
            "language": language,
            "lines": len(code.split('\n')),
            "complexity": "medium",
            "suggestions": []
        }
        
        # Use radon for Python
        if language == "python":
            try:
                from radon.complexity import cc_visit
                from radon.metrics import mi_visit
                
                complexity_results = cc_visit(code)
                analysis["complexity_score"] = sum(c.complexity for c in complexity_results)
                analysis["maintainability"] = mi_visit(code, multi=True)
            except Exception as e:
                logger.debug(f"Code analysis error: {e}")
        
        return analysis
    
    async def optimize_code(self, code: str, language: str = "python") -> str:
        """Optimize code using AI"""
        
        optimize_prompt = f"""Optimize this {language} code for better performance and readability:

{code}

Return only the optimized code without explanations."""
        
        return await self.generate_code(optimize_prompt, language, max_tokens=3000)
    
    async def fix_errors(self, code: str, errors: List[str]) -> str:
        """Fix code errors using AI"""
        
        fix_prompt = f"""Fix these errors in the code:

Errors:
{chr(10).join(errors)}

Code:
{code}

Return only the fixed code without explanations."""
        
        return await self.generate_code(fix_prompt, max_tokens=3000)
    
    async def generate_tests(self, code: str, language: str = "python") -> str:
        """Generate tests for code"""
        
        test_prompt = f"""Generate comprehensive unit tests for this {language} code:

{code}

Generate tests using pytest for Python or Jest for JavaScript.
Return only the test code."""
        
        return await self.generate_code(test_prompt, language, max_tokens=2000)
    
    async def explain_code(self, code: str) -> str:
        """Explain what code does"""
        
        explain_prompt = f"""Explain what this code does in simple terms:

{code}

Provide a clear, concise explanation."""
        
        return await self.generate_code(explain_prompt, max_tokens=500)
    
    def get_available_models(self) -> Dict[str, Any]:
        """Get list of available models"""
        return {
            "local": {
                "ollama": {
                    "available": self.ollama_available,
                    "models": ["deepseek-coder", "codellama", "mistral"] if self.ollama_available else []
                },
                "transformers": {
                    "available": self.transformers_available,
                    "models": ["CodeLlama-7b", "DeepSeek-Coder"] if self.transformers_available else []
                }
            },
            "cloud": {
                "huggingface": {
                    "available": self.hf_available,
                    "models": ["deepseek-coder", "codellama", "starcoder"] if self.hf_available else []
                },
                "replicate": {
                    "available": self.replicate_available,
                    "models": ["codellama", "llama-2"] if self.replicate_available else []
                }
            },
            "fallback": {
                "available": True,
                "description": "Template-based generation (always available)"
            }
        }
    
    async def download_model(self, model_name: str) -> bool:
        """Download model for offline use"""
        if self.ollama_available:
            try:
                import ollama
                await asyncio.to_thread(ollama.pull, model_name)
                logger.info(f"✅ Downloaded model: {model_name}")
                return True
            except Exception as e:
                logger.error(f"Failed to download {model_name}: {e}")
                return False
        return False

# Global model manager instance
model_manager = ModelManager()
