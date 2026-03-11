from pydantic import EmailStr, Field, field_validator

from src.core.schemas import (
    Base,
    EmailNormalizationMixin,
    StrongPasswordValidationMixin,
)
from src.core.validations import (
    NAME_WITH_SPACES,
    USERNAME_VALIDATOR,
)
from src.user.schemas import UserProfileViewModel


class CreateUserModel(StrongPasswordValidationMixin, EmailNormalizationMixin, Base):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    username: str
    password: str

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        if not NAME_WITH_SPACES.match(value):
            raise ValueError("Full name must contain letters, spaces, and hyphens only")
        return value

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if not USERNAME_VALIDATOR.match(value):
            raise ValueError(
                "Username must be from 4 to 60 symbols and contain alphanumeric characters, underscore, dash, and dot"
            )
        return value


class ResendVerificationModel(EmailNormalizationMixin, Base):
    email: EmailStr


class LoginUserModel(EmailNormalizationMixin, Base):
    email: EmailStr
    password: str


class SendResetPasswordRequestModel(EmailNormalizationMixin, Base):
    email: EmailStr


class ResetPasswordModel(StrongPasswordValidationMixin, Base):
    token: str
    password: str


class UserNewPassword(StrongPasswordValidationMixin, Base):
    password: str


class RegisterResponseModel(UserProfileViewModel):
    """
    Registration response.

    In DEBUG/TESTING we expose a mock verification token/link so the client/tests
    can verify the user without relying on email delivery.
    """

    verification_token: str | None = None
    verification_url: str | None = None
