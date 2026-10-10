"""Replace reset_code with magic_link_token and add is_email_verified

Revision ID: a1b2c3d4e5f6
Revises: 9e11e2fe62ac
Create Date: 2026-10-10 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "9e11e2fe62ac"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove old reset-code columns
    op.drop_column("users", "reset_code")
    op.drop_column("users", "reset_code_expiry")

    # Add magic-link columns
    op.add_column(
        "users",
        sa.Column("magic_link_token", sa.String(), nullable=True, unique=True),
    )
    op.add_column(
        "users",
        sa.Column("magic_link_token_expiry", sa.DateTime(), nullable=True),
    )
    op.create_index(
        op.f("ix_users_magic_link_token"),
        "users",
        ["magic_link_token"],
        unique=True,
    )

    # Add email-verified flag (default False for existing rows)
    op.add_column(
        "users",
        sa.Column(
            "is_email_verified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )


def downgrade() -> None:
    # Reverse: remove magic-link columns and restore reset-code columns
    op.drop_index(op.f("ix_users_magic_link_token"), table_name="users")
    op.drop_column("users", "magic_link_token_expiry")
    op.drop_column("users", "magic_link_token")
    op.drop_column("users", "is_email_verified")

    op.add_column(
        "users",
        sa.Column("reset_code", sa.String(), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("reset_code_expiry", sa.DateTime(), nullable=True),
    )
