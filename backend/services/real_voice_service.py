"""
Real Voice Service with Whisper (Speech-to-Text) and TTS (Text-to-Speech)
Supports offline (local models) and online (cloud APIs) operation
"""

import os
import asyncio
import tempfile
from typing import Optional, Dict, Any, Literal
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class RealVoiceService:
    """
    Production-ready Voice Service with multiple backends
    Priority: Local Models > Cloud APIs > Fallback
    """
    
    def __init__(self):
        self.whisper_available = self._check_whisper()
        self.tts_available = self._check_tts()
        self.elevenlabs_available = self._check_elevenlabs()
        self.google_tts_available = self._check_google_tts()
        
        # Lazy-loaded models
        self._whisper_model = None
        self._tts_model = None
        
    def _check_whisper(self) -> bool:
        """Check if Whisper is available"""
        try:
            import whisper
            return True
        except ImportError:
            logger.warning("Whisper not available. Install with: pip install openai-whisper")
            return False
    
    def _check_tts(self) -> bool:
        """Check if TTS (Coqui) is available"""
        try:
            import TTS
            return True
        except ImportError:
            logger.warning("TTS not available. Install with: pip install TTS")
            return False
    
    def _check_elevenlabs(self) -> bool:
        """Check if ElevenLabs API key is set"""
        return bool(os.getenv("ELEVENLABS_API_KEY"))
    
    def _check_google_tts(self) -> bool:
        """Check if Google Cloud TTS credentials are available"""
        return bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    
    async def speech_to_text(
        self, 
        audio_file: str,
        language: str = "en",
        model_size: Literal["tiny", "base", "small", "medium", "large"] = "base"
    ) -> Dict[str, Any]:
        """
        Convert speech to text using Whisper
        
        Args:
            audio_file: Path to audio file (wav, mp3, m4a, etc.)
            language: Language code (en, es, fr, etc.)
            model_size: Whisper model size (tiny=39M, base=74M, small=244M, medium=769M, large=1550M)
        
        Returns:
            {"text": str, "language": str, "segments": List[dict], "confidence": float}
        """
        
        # Try Whisper (local)
        if self.whisper_available:
            try:
                return await self._transcribe_with_whisper(audio_file, language, model_size)
            except Exception as e:
                logger.error(f"Whisper transcription failed: {e}")
        
        # Try Google Cloud Speech-to-Text (cloud)
        if self.google_tts_available:
            try:
                return await self._transcribe_with_google(audio_file, language)
            except Exception as e:
                logger.error(f"Google STT failed: {e}")
        
        # Fallback
        return {
            "text": "Speech recognition not available. Please install whisper or configure cloud services.",
            "language": language,
            "segments": [],
            "confidence": 0.0
        }
    
    async def _transcribe_with_whisper(
        self, 
        audio_file: str, 
        language: str,
        model_size: str
    ) -> Dict[str, Any]:
        """Transcribe audio using local Whisper model"""
        import whisper
        
        # Load model (cached after first load)
        if self._whisper_model is None or self._whisper_model.device != model_size:
            logger.info(f"Loading Whisper {model_size} model...")
            self._whisper_model = await asyncio.to_thread(whisper.load_model, model_size)
        
        # Transcribe
        logger.info(f"Transcribing audio file: {audio_file}")
        result = await asyncio.to_thread(
            self._whisper_model.transcribe,
            audio_file,
            language=language if language != "auto" else None
        )
        
        # Calculate average confidence
        avg_confidence = sum(
            seg.get("no_speech_prob", 0) for seg in result.get("segments", [])
        ) / max(len(result.get("segments", [])), 1)
        
        return {
            "text": result["text"].strip(),
            "language": result.get("language", language),
            "segments": result.get("segments", []),
            "confidence": 1.0 - avg_confidence
        }
    
    async def _transcribe_with_google(self, audio_file: str, language: str) -> Dict[str, Any]:
        """Transcribe audio using Google Cloud Speech-to-Text"""
        from google.cloud import speech
        
        client = speech.SpeechClient()
        
        # Read audio file
        with open(audio_file, "rb") as f:
            content = f.read()
        
        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            language_code=language if language != "auto" else "en-US",
            enable_automatic_punctuation=True,
        )
        
        # Transcribe
        response = await asyncio.to_thread(client.recognize, config=config, audio=audio)
        
        # Extract results
        text = " ".join(result.alternatives[0].transcript for result in response.results)
        confidence = sum(
            result.alternatives[0].confidence for result in response.results
        ) / max(len(response.results), 1)
        
        return {
            "text": text,
            "language": language,
            "segments": [{"text": r.alternatives[0].transcript} for r in response.results],
            "confidence": confidence
        }
    
    async def text_to_speech(
        self,
        text: str,
        output_file: Optional[str] = None,
        voice: str = "default",
        language: str = "en",
        speed: float = 1.0
    ) -> str:
        """
        Convert text to speech
        
        Args:
            text: Text to convert
            output_file: Output file path (auto-generated if None)
            voice: Voice ID/name
            language: Language code
            speed: Speech speed multiplier
        
        Returns:
            Path to generated audio file
        """
        
        if output_file is None:
            output_file = tempfile.mktemp(suffix=".wav")
        
        # Try TTS (Coqui) - local, high quality
        if self.tts_available:
            try:
                return await self._synthesize_with_tts(text, output_file, voice, language, speed)
            except Exception as e:
                logger.error(f"TTS synthesis failed: {e}")
        
        # Try ElevenLabs - cloud, best quality
        if self.elevenlabs_available:
            try:
                return await self._synthesize_with_elevenlabs(text, output_file, voice, speed)
            except Exception as e:
                logger.error(f"ElevenLabs TTS failed: {e}")
        
        # Try Google Cloud TTS - cloud, good quality
        if self.google_tts_available:
            try:
                return await self._synthesize_with_google(text, output_file, language, speed)
            except Exception as e:
                logger.error(f"Google TTS failed: {e}")
        
        # Try gTTS (basic, always available)
        try:
            return await self._synthesize_with_gtts(text, output_file, language)
        except Exception as e:
            logger.error(f"gTTS synthesis failed: {e}")
        
        # Fallback - create empty file
        Path(output_file).touch()
        return output_file
    
    async def _synthesize_with_tts(
        self, 
        text: str, 
        output_file: str,
        voice: str,
        language: str,
        speed: float
    ) -> str:
        """Synthesize speech using Coqui TTS (local)"""
        from TTS.api import TTS as CoquiTTS
        
        # Initialize TTS model (cached)
        if self._tts_model is None:
            logger.info("Loading TTS model...")
            # Use fast, multilingual model
            model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
            self._tts_model = await asyncio.to_thread(CoquiTTS, model_name=model_name)
        
        # Synthesize
        logger.info(f"Synthesizing speech: {text[:50]}...")
        await asyncio.to_thread(
            self._tts_model.tts_to_file,
            text=text,
            file_path=output_file,
            language=language,
            speed=speed
        )
        
        return output_file
    
    async def _synthesize_with_elevenlabs(
        self, 
        text: str, 
        output_file: str,
        voice: str,
        speed: float
    ) -> str:
        """Synthesize speech using ElevenLabs API"""
        from elevenlabs import generate, save
        
        api_key = os.getenv("ELEVENLABS_API_KEY")
        
        # Generate audio
        audio = await asyncio.to_thread(
            generate,
            text=text,
            voice=voice if voice != "default" else "Adam",
            api_key=api_key
        )
        
        # Save to file
        await asyncio.to_thread(save, audio, output_file)
        
        return output_file
    
    async def _synthesize_with_google(
        self, 
        text: str, 
        output_file: str,
        language: str,
        speed: float
    ) -> str:
        """Synthesize speech using Google Cloud TTS"""
        from google.cloud import texttospeech
        
        client = texttospeech.TextToSpeechClient()
        
        # Configure synthesis
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=language,
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=speed
        )
        
        # Synthesize
        response = await asyncio.to_thread(
            client.synthesize_speech,
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # Save to file
        with open(output_file, "wb") as f:
            f.write(response.audio_content)
        
        return output_file
    
    async def _synthesize_with_gtts(self, text: str, output_file: str, language: str) -> str:
        """Synthesize speech using gTTS (basic, always available)"""
        from gtts import gTTS
        
        tts = gTTS(text=text, lang=language, slow=False)
        await asyncio.to_thread(tts.save, output_file)
        
        return output_file
    
    async def get_available_voices(self) -> Dict[str, Any]:
        """Get list of available voices"""
        voices = {"local": [], "cloud": []}
        
        if self.tts_available:
            try:
                from TTS.api import TTS as CoquiTTS
                tts = CoquiTTS()
                voices["local"] = tts.list_models()
            except Exception as e:
                logger.error(f"Failed to list TTS models: {e}")
        
        if self.elevenlabs_available:
            try:
                from elevenlabs import voices as elevenlabs_voices
                api_key = os.getenv("ELEVENLABS_API_KEY")
                voice_list = await asyncio.to_thread(elevenlabs_voices, api_key=api_key)
                voices["cloud"].extend([{"id": v.voice_id, "name": v.name} for v in voice_list])
            except Exception as e:
                logger.error(f"Failed to list ElevenLabs voices: {e}")
        
        return voices
    
    def get_status(self) -> Dict[str, Any]:
        """Get voice service status"""
        return {
            "speech_to_text": {
                "whisper": self.whisper_available,
                "google_stt": self.google_tts_available,
                "status": "available" if (self.whisper_available or self.google_tts_available) else "unavailable"
            },
            "text_to_speech": {
                "tts_coqui": self.tts_available,
                "elevenlabs": self.elevenlabs_available,
                "google_tts": self.google_tts_available,
                "gtts": True,  # Always available as fallback
                "status": "available"
            }
        }


# Singleton instance
voice_service = RealVoiceService()
