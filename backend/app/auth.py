import base64
import hashlib
import hmac
import os
import secrets
import time

SECRET = os.getenv("TRAGERAG_AUTH_SECRET", "change-this-secret-in-production").encode()
TOKEN_TTL = 60 * 60 * 8


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 210_000)
    return f"{base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_text, digest_text = stored.split("$", 1)
        salt = base64.urlsafe_b64decode(salt_text.encode())
        expected = base64.urlsafe_b64decode(digest_text.encode())
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 210_000)
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_token(email: str) -> str:
    payload = f"{email}|{int(time.time()) + TOKEN_TTL}"
    signature = hmac.new(SECRET, payload.encode(), hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(f"{payload}|{signature}".encode()).decode()


def read_token(token: str) -> str | None:
    try:
        decoded = base64.urlsafe_b64decode(token.encode()).decode()
        email, expiry, signature = decoded.rsplit("|", 2)
        payload = f"{email}|{expiry}"
        valid_signature = hmac.compare_digest(signature, hmac.new(SECRET, payload.encode(), hashlib.sha256).hexdigest())
        return email if int(expiry) >= time.time() and valid_signature else None
    except (ValueError, TypeError, UnicodeDecodeError):
        return None
