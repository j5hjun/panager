from cryptography.fernet import Fernet
from app.core.config import settings

# In a real production app, ensure SECRET_KEY is a valid Fernet key (32 url-safe base64-encoded bytes)
# For now, we'll generate one if the provided key is not valid, OR just trust the user provided a valid one.
# To keep it simple for MVP and avoid "InvalidToken" errors if key changes,
# let's assume settings.SECRET_KEY is used as a consistent seed or we use a dedicated key.


def _get_fernet() -> Fernet:
    """
    Ensure we have a valid Fernet key.
    If SECRET_KEY isn't compliant, this might raise an error.
    For this MVP, we assume the user provides a valid key or we handle it.
    """
    try:
        return Fernet(settings.SECRET_KEY)
    except Exception:
        # Fallback for dev if the key in .env isn't a valid fernet key
        # In PROD, this should fail loudly.
        # Construct a valid key from the secret by padding/hashing if needed,
        # or just fail. Let's fail loudly to enforce good config.
        raise ValueError(
            "SECRET_KEY must be a valid 32-byte base64url-encoded string for Fernet."
        )


def encrypt_token(token: str) -> str:
    """Encrypt a raw token string."""
    f = _get_fernet()
    return f.encrypt(token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt an encrypted token string."""
    f = _get_fernet()
    return f.decrypt(encrypted_token.encode()).decode()
