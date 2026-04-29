"""Unit tests for core.security password hashing."""

from core.security import get_bcrypt_context


def test_get_bcrypt_context_hash_and_verify() -> None:
    ctx = get_bcrypt_context()
    raw = "TestP@ssw0rd!"
    hashed = ctx.hash(raw)
    assert hashed != raw
    assert ctx.verify(raw, hashed) is True
    assert ctx.verify("wrong", hashed) is False
