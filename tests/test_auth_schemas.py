"""Unit tests for Pydantic auth schemas."""

import pytest
from pydantic import ValidationError

from application.schemas.auth_schemas import ChangePasswordRequest, CreateUserRequest


def test_create_user_strong_password() -> None:
    req = CreateUserRequest(
        first_name="A",
        last_name="B",
        middle_name="",
        email="a@example.com",
        password="Str0ng!pass",
    )
    assert req.password == "Str0ng!pass"


@pytest.mark.parametrize(
    "password",
    [
        "Password12",
        "PASSWORD12!",
        "nopassword!",
        "NOLOWCASE1!",
    ],
)
def test_create_user_weak_password_rejected(password: str) -> None:
    with pytest.raises(ValidationError):
        CreateUserRequest(
            first_name="A",
            last_name="B",
            middle_name="",
            email="a@example.com",
            password=password,
        )


def test_change_password_new_must_be_strong() -> None:
    with pytest.raises(ValidationError):
        ChangePasswordRequest(current_password="x", new_password="weakpass")


def test_change_password_acceptable() -> None:
    ChangePasswordRequest(current_password="old", new_password="NewStr0ng!x")
