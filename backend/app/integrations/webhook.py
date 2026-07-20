import hashlib
import hmac


def verify(secret: str, body: bytes, signature: str) -> bool:
    return hmac.compare_digest(
        hmac.new(secret.encode(), body, hashlib.sha256).hexdigest(), signature
    )
