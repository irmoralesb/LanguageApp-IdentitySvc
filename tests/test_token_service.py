"""Unit tests for application.services.token_service.TokenService."""

from datetime import timedelta, timezone
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import jwt
import pytest

from application.services.token_service import TokenService
from domain.entities.role_model import RoleModel
from domain.entities.service_model import ServiceModel
from domain.entities.user_model import UserModel, UserWithRolesModel


@pytest.fixture
def repos() -> tuple[AsyncMock, AsyncMock, AsyncMock]:
    return AsyncMock(), AsyncMock(), AsyncMock()


@pytest.fixture
def token_service(repos):
    role_repo, user_repo, service_repo = repos
    return TokenService(
        secret_key="secret-key-unit-test-placeholder-32chars",
        algorithm="HS256",
        role_repo=role_repo,
        user_repo=user_repo,
        service_repo=service_repo,
    )


@pytest.mark.asyncio
async def test_get_user_raises_when_user_missing(token_service: TokenService, repos) -> None:
    _, user_repo, _ = repos
    uid = uuid4()
    user_repo.get_by_id.return_value = None
    payload = jwt.encode(
        {"sub": str(uid), "email": "e@test.com"}, "secret-key-unit-test-placeholder-32chars", algorithm="HS256"
    )
    with pytest.raises(ValueError, match="Cannot read the user"):
        await token_service.get_user(payload)


@pytest.mark.asyncio
async def test_get_user_raises_when_no_roles(token_service: TokenService, repos) -> None:
    role_repo, user_repo, _ = repos
    uid = uuid4()
    user = UserModel(id=uid, first_name="A", last_name="B", email="a@test.com")
    user_repo.get_by_id.return_value = user
    role_repo.get_user_roles.return_value = []
    payload = jwt.encode(
        {"sub": str(uid)}, "secret-key-unit-test-placeholder-32chars", algorithm="HS256"
    )
    with pytest.raises(ValueError, match="roles"):
        await token_service.get_user(payload)


@pytest.mark.asyncio
async def test_get_user_success(token_service: TokenService, repos) -> None:
    role_repo, user_repo, _ = repos
    uid = uuid4()
    user = UserModel(id=uid, first_name="A", last_name="B", email="a@test.com")
    srv_id = uuid4()
    role = RoleModel(id=uuid4(), name="user", description="d", service_id=srv_id)
    user_repo.get_by_id.return_value = user
    role_repo.get_user_roles.return_value = [role]
    payload = jwt.encode(
        {"sub": str(uid)}, "secret-key-unit-test-placeholder-32chars", algorithm="HS256"
    )
    out = await token_service.get_user(payload)
    assert isinstance(out, UserWithRolesModel)
    assert out.user.email == "a@test.com"


@pytest.mark.asyncio
async def test_create_access_token_raises_without_user_id(
    token_service: TokenService, repos
) -> None:
    user = UserModel(id=None, first_name="A", last_name="B", email="a@test.com")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="null"):
        await token_service.create_access_token(user)


@pytest.mark.asyncio
async def test_create_access_token_builds_claims(monkeypatch, token_service: TokenService, repos) -> None:
    monkeypatch.setattr(
        "infrastructure.observability.metrics.prometheus.record_token_metrics",
        lambda **kwargs: None,
    )

    uid = uuid4()
    srv_id = uuid4()
    user = UserModel(id=uid, first_name="A", last_name="B", email="u@test.com")
    role_repo, _, service_repo = repos

    role_repo.get_user_roles.return_value = [
        RoleModel(id=uuid4(), name="teacher", description="d", service_id=srv_id)
    ]
    service_repo.get_by_id.return_value = ServiceModel(
        id=srv_id,
        name="phrasal-verbs",
        description=None,
        is_active=True,
        url=None,
        port=None,
    )

    token = await token_service.create_access_token(user, timedelta(hours=1))
    decoded = jwt.decode(token, token_service.secret_key, algorithms=["HS256"])
    assert decoded["email"] == "u@test.com"
    assert str(uid) == decoded["sub"]
    assert "phrasal-verbs" in decoded["roles"]
    assert decoded["roles"]["phrasal-verbs"] == ["teacher"]
