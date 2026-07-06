import base64
import hashlib

from cryptography.fernet import Fernet
from fastapi import HTTPException, status

from app.core.config import settings


def _fernet() -> Fernet:
    if not settings.encryption_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Encryption key is not configured",
        )
    digest = hashlib.sha256(settings.encryption_key.encode("utf-8")).digest()
    key = base64.urlsafe_b64encode(digest)
    return Fernet(key)


def encrypt_secret(value: str) -> str:
    return _fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_secret(value: str) -> str:
    return _fernet().decrypt(value.encode("utf-8")).decode("utf-8")
