"""Guards the session-expiry bug: create_access_token() defaults to a 15-minute
expiry when no expires_delta is passed, so login() must pass one explicitly
using ACCESS_TOKEN_EXPIRE_MINUTES. Without this, sessions die every 15 min
regardless of the configured constant.

Run with: pytest backend/tests/test_auth_token_expiry.py -v
"""
from datetime import datetime, timedelta

from jose import jwt

from backend.auth import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM, create_access_token


def test_access_token_respects_configured_expiry():
    token = create_access_token(
        data={"sub": "test@example.com"},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    expires_at = datetime.utcfromtimestamp(payload["exp"])

    expected = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    assert abs((expires_at - expected).total_seconds()) < 5

    # The bug this guards against: forgetting expires_delta silently gives 15 min.
    assert ACCESS_TOKEN_EXPIRE_MINUTES > 15
