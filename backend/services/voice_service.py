"""
Voice Service
Handles voice interaction using:
- Whisper for speech-to-text
- TTS/Piper for text-to-speech
- Integration with Chatterbox
"""

import os
import logging
import base64
from typing import Optional
import asyncio

logger = logging.getLogger(__name__)

class VoiceService:
    """Service for voice interaction capabilities"""
    
    def __init__(self):
        self.whisper_available = False
        self.tts_available = False
        self._check_availability()
    
    def _check_availability(self):
        """Check if voice services are available"""
        try:
            # Check for Whisper
            import whisper
            self.whisper_available = True
            logger.info("Whisper available for speech-to-text")
        except ImportError:
            logger.info("Whisper not available")
        
        try:
            # Check for TTS
            import TTS
            self.tts_available = True
            logger.info("TTS available for text-to-speech")
        except ImportError:
            logger.info("TTS not available")
    
    def is_available(self) -> bool:
        """Check if voice services are available"""
        return self.whisper_available or self.tts_available
    
    async def transcribe(self, audio_data: str) -> str:
        """
        Transcribe audio to text using Whisper
        
        Args:
            audio_data: Base64 encoded audio data
            
        Returns:
            Transcribed text
        """
        if not self.whisper_available:
            raise Exception("Whisper not available. Install with: pip install whisper")
        
        try:
            import whisper
            import tempfile
            
            # Decode base64 audio
            audio_bytes = base64.b64decode(audio_data)
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                temp_audio.write(audio_bytes)
                temp_path = temp_audio.name
            
            # Load model (use base model for speed)
            model = whisper.load_model("base")
            
            # Transcribe
            result = await asyncio.to_thread(model.transcribe, temp_path)
            
            # Cleanup
            os.unlink(temp_path)
            
            return result["text"]
        
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            raise Exception(f"Failed to transcribe audio: {str(e)}")
    
    async def synthesize(self, text: str, voice: Optional[str] = None) -> str:
        """
        Synthesize speech from text
        
        Args:
            text: Text to convert to speech
            voice: Voice ID/model to use (optional)
            
        Returns:
            Base64 encoded audio data
        """
        if not self.tts_available:
            raise Exception("TTS not available. Install with: pip install TTS")
        
        try:
            from TTS.api import TTS
            import tempfile
            
            # Initialize TTS
            tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
            
            # Generate audio to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                temp_path = temp_audio.name
            
            await asyncio.to_thread(tts.tts_to_file, text=text, file_path=temp_path)
            
            # Read and encode
            with open(temp_path, "rb") as f:
                audio_bytes = f.read()
            
            # Cleanup
            os.unlink(temp_path)
            
            # Encode to base64
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            return audio_base64
        
        except Exception as e:
            logger.error(f"Synthesis error: {str(e)}")
            raise Exception(f"Failed to synthesize speech: {str(e)}")
    
    async def process_chatterbox_integration(self):
        """
        Integrate with Chatterbox voice system
        GitHub: https://github.com/chatterbox-ai/chatterbox
        
        This will be implemented based on the actual Chatterbox API
        """
        logger.info("Chatterbox integration placeholder - add GitHub link to implement")
        pass
