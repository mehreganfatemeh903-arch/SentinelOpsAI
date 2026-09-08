import hashlib
import secrets

PREFIX = 'sntl_' 

def generate_api_key() -> tuple[str, str]:
    raw = PREFIX + secrets.token_urlsafe(32)
    return raw, hashlib.sha256(raw.encode()).hexdigest()

def hash_api_key(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()
