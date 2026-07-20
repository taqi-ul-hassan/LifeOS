import base64, hashlib
from cryptography.fernet import Fernet
from ..config import get_settings
def cipher() -> Fernet: return Fernet(base64.urlsafe_b64encode(hashlib.sha256(get_settings().jwt_secret.encode()).digest()))
def encrypt(value: dict) -> str: import json; return cipher().encrypt(json.dumps(value).encode()).decode()
def decrypt(value: str) -> dict: import json; return json.loads(cipher().decrypt(value.encode()))
