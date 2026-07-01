"""
Data encryption utilities for HIPAA compliance.
AES-256 encryption for data at rest.
"""

import base64
import logging

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.config import get_settings

logger = logging.getLogger(__name__)


class EncryptionManager:
    """AES-256 encryption for sensitive data at rest."""

    _instance = None
    _cipher = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _initialize(self):
        """Initialize encryption with the configured key."""
        if self._cipher is None:
            settings = get_settings()

            if settings.encryption_key:
                # Derive a proper key from the configured encryption key
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=b"healthcare-navigator-salt",
                    iterations=100_000,
                )
                key = base64.urlsafe_b64encode(
                    kdf.derive(settings.encryption_key.encode())
                )
            else:
                # Generate a key for development (not persistent across restarts)
                key = Fernet.generate_key()
                logger.warning(
                    "⚠️  Using auto-generated encryption key. "
                    "Set ENCRYPTION_KEY in .env for persistent encryption."
                )

            self._cipher = Fernet(key)

    def encrypt(self, data: str) -> str:
        """Encrypt a string and return base64-encoded ciphertext."""
        self._initialize()
        encrypted = self._cipher.encrypt(data.encode("utf-8"))
        return base64.urlsafe_b64encode(encrypted).decode("utf-8")

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt base64-encoded ciphertext and return plaintext."""
        self._initialize()
        raw = base64.urlsafe_b64decode(encrypted_data.encode("utf-8"))
        return self._cipher.decrypt(raw).decode("utf-8")


def get_encryption_manager() -> EncryptionManager:
    """Get singleton encryption manager."""
    return EncryptionManager()
