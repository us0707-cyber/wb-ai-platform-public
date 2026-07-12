import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from src.core.config import settings


def _fernet() -> Fernet:
    digest = hashlib.sha256(settings.secret_key.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt_token(token: str) -> str:
    if not token:
        return ""
    return _fernet().encrypt(token.encode("utf-8")).decode("utf-8")


def decrypt_token(value: str) -> str:
    if not value:
        return ""
    try:
        return _fernet().decrypt(value.encode("utf-8")).decode("utf-8")
    except (InvalidToken, ValueError):
        # Backward compatibility for old plaintext records.
        return value
