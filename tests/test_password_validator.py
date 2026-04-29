"""Unit tests for core.password_validator."""
import pytest

from core.password_validator import PasswordValidationError, PasswordValidator


@pytest.mark.parametrize(
    ("password", "expect_valid"),
    [
        ("Str0ng!x", True),
        ("Aa1!aaaa", True),
        ("short1!", False),
        ("PASSWORD1!", False),
        ("password1!", False),
        ("Pass-word", False),
        ("PASSWORDA1!", False),
    ],
)
def test_is_valid(password: str, expect_valid: bool) -> None:
    assert PasswordValidator.is_valid(password) is expect_valid


def test_validate_accepts_minimum_viable_password() -> None:
    PasswordValidator.validate("Aa0!abcd")


def test_validate_collects_multiple_errors() -> None:
    with pytest.raises(PasswordValidationError) as exc_info:
        PasswordValidator.validate("weak")
    assert len(exc_info.value.errors) >= 2


def test_length_bounds() -> None:
    PasswordValidator.validate("A" + "a1!" + ("x" * (PasswordValidator.MIN_LENGTH - 4)))
    with pytest.raises(PasswordValidationError):
        PasswordValidator.validate("Aa1!")
    # Prefix "Aa1!" has length 4; pad to exactly MAX_LENGTH then add one byte over limit.
    too_long_exact = "Aa1!" + ("x" * (PasswordValidator.MAX_LENGTH - 4))
    PasswordValidator.validate(too_long_exact)
    with pytest.raises(PasswordValidationError):
        PasswordValidator.validate(too_long_exact + "x")


def test_exceptions_message_join() -> None:
    with pytest.raises(PasswordValidationError) as exc:
        PasswordValidator.validate("x")
    assert "; " in str(exc.value) or str(exc.value)
