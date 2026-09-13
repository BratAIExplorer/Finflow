"""
Encrypts/decrypts broker credentials (API keys, TOTP secrets) before they touch the DB.
Never store these in plaintext — a Holding is read-only, but the credentials that
produce it can do more than read on the broker's side, so they get the same care
as a password.
"""
import os
import json
from cryptography.fernet import Fernet


def _get_fernet() -> Fernet:
    key = os.getenv("APP_ENCRYPTION_KEY")
    if not key:
        raise RuntimeError(
            "APP_ENCRYPTION_KEY is not set. Generate one with: "
            "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\" "
            "and put it in your .env — losing this key makes stored broker credentials unrecoverable."
        )
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_credentials(data: dict) -> str:
    """dict -> encrypted string, safe to store in a JSON/String column."""
    f = _get_fernet()
    return f.encrypt(json.dumps(data).encode()).decode()


def decrypt_credentials(token: str) -> dict:
    """encrypted string -> dict. Raises cryptography.fernet.InvalidToken if the key is wrong."""
    f = _get_fernet()
    return json.loads(f.decrypt(token.encode()).decode())
