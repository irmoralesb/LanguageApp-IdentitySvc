"""
- Install a stub ``infrastructure.databases.database`` before any test imports
  repositories/models. The real module starts SQLAlchemy at import time and is
  not suitable for isolated unit tests.
- Set defaults for optional ``pytest_configure`` hooks that expect env (if
  ``core.settings`` is ever imported).
"""

from __future__ import annotations

import os
import sys
import uuid
from contextlib import asynccontextmanager
from types import ModuleType


def _stub_infrastructure_database() -> None:
    key = "infrastructure.databases.database"
    if key in sys.modules:
        return

    from sqlalchemy.orm import declarative_base

    stub = ModuleType(key)

    @asynccontextmanager
    async def get_monitored_db_session():
        raise RuntimeError(
            "DB session should not run in stubbed database unit-test context"
        )

    stub.Base = declarative_base()
    stub.engine = None
    stub.AsyncSessionLocal = None
    stub.IDENTITY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    stub.IDENTITY_DATABASE_MIGRATION_URL = "sqlite:///:memory:"
    stub.get_monitored_db_session = get_monitored_db_session
    sys.modules[key] = stub


_stub_infrastructure_database()


def pytest_configure():
    oid = str(uuid.UUID(int=100))
    defaults = {
        "SECRET_TOKEN_KEY": "x" * 40,
        "AUTH_ALGORITHM": "HS256",
        "TOKEN_TIME_DELTA_IN_MINUTES": "60",
        "IDENTITY_DATABASE_URL": "mssql+pyodbc://user:pass@localhost/identity_db",
        "IDENTITY_DATABASE_MIGRATION_URL": (
            "mssql+pyodbc://user:pass@localhost/identity_migration"
        ),
        "DEFAULT_USER_ROLE": "user",
        "TOKEN_URL": "/token",
        "SERVICE_ID": oid,
    }
    for k, val in defaults.items():
        os.environ.setdefault(k, val)
