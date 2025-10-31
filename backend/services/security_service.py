"""
Security Service for API Key Encryption and Secure Storage
Uses Fernet symmetric encryption with environment-based secret key
"""

import os
import base64
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import logging

logger = logging.getLogger(__name__)


class SecurityService:
    """
    Handles encryption/decryption of sensitive data like API keys
    Uses Fernet (symmetric encryption) with key derived from environment secret
    """
    
    def __init__(self):
        self._fernet = None
        self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Initialize Fernet encryption with secret key"""
        # Get secret key from environment or generate one
        secret_key = os.getenv("ENCRYPTION_SECRET_KEY")
        
        if not secret_key:
            logger.warning(
                "ENCRYPTION_SECRET_KEY not set! Generating a new key. "
                "SET THIS IN PRODUCTION: export ENCRYPTION_SECRET_KEY=<your-secret-key>"
            )
            secret_key = Fernet.generate_key().decode()
            logger.info(f"Generated key (SAVE THIS): {secret_key}")
        
        # Derive encryption key from secret
        if isinstance(secret_key, str):
            secret_key = secret_key.encode()
        
        # Use PBKDF2 to derive a proper Fernet key
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'universal_ai_app_generator_salt',  # Static salt for consistency
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret_key))
        
        self._fernet = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt a string
        
        Args:
            data: Plain text to encrypt
        
        Returns:
            Encrypted string (base64 encoded)
        """
        if not data:
            return ""
        
        try:
            encrypted = self._fernet.encrypt(data.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt an encrypted string
        
        Args:
            encrypted_data: Encrypted string (base64 encoded)
        
        Returns:
            Decrypted plain text
        """
        if not encrypted_data:
            return ""
        
        try:
            decrypted = self._fernet.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def encrypt_api_key(self, api_key: str, service: str) -> str:
        """
        Encrypt an API key for storage
        
        Args:
            api_key: The API key to encrypt
            service: Service name (for logging)
        
        Returns:
            Encrypted API key
        """
        logger.info(f"Encrypting API key for service: {service}")
        return self.encrypt(api_key)
    
    def decrypt_api_key(self, encrypted_key: str, service: str) -> str:
        """
        Decrypt an API key for use
        
        Args:
            encrypted_key: Encrypted API key
            service: Service name (for logging)
        
        Returns:
            Decrypted API key
        """
        logger.info(f"Decrypting API key for service: {service}")
        return self.decrypt(encrypted_key)
    
    def validate_api_key_format(self, service: str, api_key: str) -> bool:
        """
        Validate API key format for different services
        
        Args:
            service: Service name
            api_key: API key to validate
        
        Returns:
            True if format is valid
        """
        validators = {
            "huggingface": lambda k: k.startswith("hf_") and len(k) > 20,
            "openai": lambda k: k.startswith("sk-") and len(k) > 20,
            "replicate": lambda k: len(k) == 40,
            "elevenlabs": lambda k: len(k) > 20,
            "google": lambda k: len(k) > 20,
            "anthropic": lambda k: k.startswith("sk-ant-") and len(k) > 20,
        }
        
        validator = validators.get(service.lower())
        if validator:
            return validator(api_key)
        
        # Default validation - just check it's not empty
        return bool(api_key and len(api_key) > 10)
    
    def mask_api_key(self, api_key: str, show_chars: int = 4) -> str:
        """
        Mask API key for display (show only last N characters)
        
        Args:
            api_key: API key to mask
            show_chars: Number of characters to show at the end
        
        Returns:
            Masked API key (e.g., "sk-****1234")
        """
        if not api_key or len(api_key) <= show_chars:
            return "****"
        
        prefix = api_key[:3] if len(api_key) > 10 else ""
        suffix = api_key[-show_chars:]
        return f"{prefix}{'*' * (len(api_key) - len(prefix) - show_chars)}{suffix}"
    
    def generate_secure_token(self, length: int = 32) -> str:
        """
        Generate a secure random token
        
        Args:
            length: Token length in bytes
        
        Returns:
            Secure random token (hex encoded)
        """
        import secrets
        return secrets.token_hex(length)
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt
        
        Args:
            password: Plain text password
        
        Returns:
            Hashed password
        """
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password
        
        Returns:
            True if password matches
        """
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_encryption_info(self) -> Dict[str, Any]:
        """Get encryption system information"""
        return {
            "encryption_enabled": self._fernet is not None,
            "algorithm": "Fernet (AES-128-CBC with HMAC)",
            "key_derivation": "PBKDF2-SHA256 (100k iterations)",
            "status": "active" if self._fernet else "inactive"
        }


# Singleton instance
security_service = SecurityService()


# Helper functions for easy import
def encrypt_api_key(api_key: str, service: str) -> str:
    """Encrypt an API key"""
    return security_service.encrypt_api_key(api_key, service)


def decrypt_api_key(encrypted_key: str, service: str) -> str:
    """Decrypt an API key"""
    return security_service.decrypt_api_key(encrypted_key, service)


def mask_api_key(api_key: str) -> str:
    """Mask an API key for display"""
    return security_service.mask_api_key(api_key)


def validate_api_key_format(service: str, api_key: str) -> bool:
    """Validate API key format"""
    return security_service.validate_api_key_format(service, api_key)
