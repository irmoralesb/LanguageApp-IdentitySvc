"""Seed prepositions-service RBAC for LanguageApp-PrepositionsSvc.

Revision ID: 20260428_0002
Revises: 20260216_0001
Create Date: 2026-04-28

Inserts service ``prepositions-service`` with roles ``prepositions-user`` and ``admin``,
then assigns both roles and the service to the seed admin user (matched by ADMIN_EMAIL).
"""
from __future__ import annotations

import os
import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from dotenv import load_dotenv
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER

revision: str = "20260428_0002"
down_revision: Union[str, Sequence[str], None] = "20260216_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PREPOSITIONS_SERVICE_ID = uuid.UUID("c0000002-0000-0000-0000-000000000001")
PREPOSITIONS_USER_ROLE_ID = uuid.UUID("c0000002-0000-0000-0000-000000000011")
PREPOSITIONS_ADMIN_ROLE_ID = uuid.UUID("c0000002-0000-0000-0000-000000000012")


def upgrade() -> None:
    load_dotenv()
    services_table = sa.table(
        "services",
        sa.column("id", UNIQUEIDENTIFIER(as_uuid=True)),
        sa.column("name", sa.String(50)),
        sa.column("description", sa.String(255)),
        sa.column("is_active", sa.Boolean),
        sa.column("url", sa.String(255)),
        sa.column("port", sa.Integer),
    )
    op.bulk_insert(
        services_table,
        [
            {
                "id": PREPOSITIONS_SERVICE_ID,
                "name": "prepositions-service",
                "description": "LanguageApp Prepositions practice API",
                "is_active": True,
                "url": None,
                "port": None,
            }
        ],
    )

    roles_table = sa.table(
        "roles",
        sa.column("id", UNIQUEIDENTIFIER(as_uuid=True)),
        sa.column("service_id", UNIQUEIDENTIFIER(as_uuid=True)),
        sa.column("name", sa.String(50)),
        sa.column("description", sa.String(200)),
        sa.column("is_active", sa.Boolean),
    )
    op.bulk_insert(
        roles_table,
        [
            {
                "id": PREPOSITIONS_USER_ROLE_ID,
                "service_id": PREPOSITIONS_SERVICE_ID,
                "name": "prepositions-user",
                "description": "Can use the Prepositions practice API",
                "is_active": True,
            },
            {
                "id": PREPOSITIONS_ADMIN_ROLE_ID,
                "service_id": PREPOSITIONS_SERVICE_ID,
                "name": "admin",
                "description": "Catalog administrator for Prepositions service",
                "is_active": True,
            },
        ],
    )

    admin_email = os.getenv("ADMIN_EMAIL", "admin@email.com")
    conn = op.get_bind()
    row = conn.execute(
        sa.text("SELECT id FROM users WHERE email = :email AND COALESCE(is_deleted, 0) = 0"),
        {"email": admin_email},
    ).fetchone()
    admin_id = row[0] if row else None

    if admin_id is not None:
        user_roles_table = sa.table(
            "user_roles",
            sa.column("id", UNIQUEIDENTIFIER(as_uuid=True)),
            sa.column("user_id", UNIQUEIDENTIFIER(as_uuid=True)),
            sa.column("role_id", UNIQUEIDENTIFIER(as_uuid=True)),
        )
        op.bulk_insert(
            user_roles_table,
            [
                {
                    "id": uuid.uuid4(),
                    "user_id": admin_id,
                    "role_id": PREPOSITIONS_USER_ROLE_ID,
                },
                {
                    "id": uuid.uuid4(),
                    "user_id": admin_id,
                    "role_id": PREPOSITIONS_ADMIN_ROLE_ID,
                },
            ],
        )
        user_services_table = sa.table(
            "user_services",
            sa.column("id", UNIQUEIDENTIFIER(as_uuid=True)),
            sa.column("user_id", UNIQUEIDENTIFIER(as_uuid=True)),
            sa.column("service_id", UNIQUEIDENTIFIER(as_uuid=True)),
        )
        op.bulk_insert(
            user_services_table,
            [
                {
                    "id": uuid.uuid4(),
                    "user_id": admin_id,
                    "service_id": PREPOSITIONS_SERVICE_ID,
                }
            ],
        )


def downgrade() -> None:
    r1, r2 = str(PREPOSITIONS_USER_ROLE_ID), str(PREPOSITIONS_ADMIN_ROLE_ID)
    sid = str(PREPOSITIONS_SERVICE_ID)
    op.execute(sa.text(f"DELETE FROM user_roles WHERE role_id IN ('{r1}', '{r2}')"))
    op.execute(sa.text(f"DELETE FROM user_services WHERE service_id = '{sid}'"))
    op.execute(sa.text(f"DELETE FROM roles WHERE service_id = '{sid}'"))
    op.execute(sa.text(f"DELETE FROM services WHERE id = '{sid}'"))
