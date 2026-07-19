import base64
import hashlib
from datetime import datetime, timedelta, timezone
from cryptography.fernet import Fernet
import jwt
from fastapi import HTTPException, status
from pwdlib import PasswordHash
from .config import get_settings

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def create_access_token(subject: str) -> str:
    settings = get_settings()
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_minutes
    )
    return jwt.encode(
        {"sub": subject, "exp": expires, "iat": datetime.now(timezone.utc)},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> str:
    try:
        return str(
            jwt.decode(
                token,
                get_settings().jwt_secret,
                algorithms=[get_settings().jwt_algorithm],
            )["sub"]
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        ) from exc


def encrypt_credential(value: str | None) -> str | None:
    if value is None:
        return None
    key = base64.urlsafe_b64encode(
        hashlib.sha256(get_settings().jwt_secret.encode()).digest()
    )
    return Fernet(key).encrypt(value.encode()).decode()
