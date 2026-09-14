"""Admin CLI to reset a user's password directly in the DB.

No email service exists yet, so this is the "forgot password" path for now:
run it yourself instead of clicking an email link.

Usage:
    python -m backend.tools.reset_password you@example.com "NewPassword123"
"""
import sys

from ..database import SessionLocal
from ..models import User
from ..auth import get_password_hash


def reset_password(email: str, new_password: str) -> None:
    if len(new_password) < 8:
        raise ValueError("Password must be at least 8 characters")

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise ValueError(f"No user found with email {email!r}")
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        print(f"Password updated for {email}")
    finally:
        db.close()


def demo() -> None:
    """Self-check: confirm a password change actually verifies afterward."""
    from ..auth import verify_password

    db = SessionLocal()
    try:
        test_user = db.query(User).first()
        if not test_user:
            print("No users in DB — skipping demo() self-check")
            return
        original_hash = test_user.hashed_password
        reset_password(test_user.email, "TempCheck1234")
        db.refresh(test_user)
        assert verify_password("TempCheck1234", test_user.hashed_password)
        test_user.hashed_password = original_hash
        db.commit()
        print("demo() OK: reset + verify round-trip works")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--demo":
        demo()
    elif len(sys.argv) == 3:
        reset_password(sys.argv[1], sys.argv[2])
    else:
        print(__doc__)
        sys.exit(1)
