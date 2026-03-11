import pytest

from src.user.enums import UserRole
from src.user.models import User


def test_user_password_hash_requires_hash() -> None:
    with pytest.raises(ValueError, match="Password hash must be a valid hash."):
        User(
            full_name="John Doe",
            email="john@example.com",
            username="john_doe",
            password_hash="plain-password",
            role=UserRole.VIEWER,
            is_verified=False,
            is_active=True,
        )
