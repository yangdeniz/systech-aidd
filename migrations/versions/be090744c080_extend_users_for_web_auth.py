"""extend users for web auth

Revision ID: be090744c080
Revises: 8160fed5c5f0
Create Date: 2025-10-17 19:56:39.841850

"""

import os
from collections.abc import Sequence

import bcrypt
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "be090744c080"
down_revision: str | Sequence[str] | None = "8160fed5c5f0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Step 1: Create enum types
    user_type_enum = sa.Enum("telegram", "web", name="user_type_enum")
    user_role_enum = sa.Enum("user", "administrator", name="user_role_enum")
    user_type_enum.create(op.get_bind(), checkfirst=True)
    user_role_enum.create(op.get_bind(), checkfirst=True)

    # Step 2: Add new columns
    # user_type with default 'telegram'
    op.add_column(
        "users",
        sa.Column(
            "user_type",
            user_type_enum,
            nullable=False,
            server_default="telegram",
        ),
    )
    # password_hash (nullable, only for web users)
    op.add_column(
        "users",
        sa.Column("password_hash", sa.String(length=255), nullable=True),
    )
    # role (nullable, only for web users)
    op.add_column(
        "users",
        sa.Column("role", user_role_enum, nullable=True),
    )
    # last_login (nullable, for web users)
    op.add_column(
        "users",
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
    )

    # Step 3: Make telegram_id nullable (required for web users)
    op.alter_column(
        "users",
        "telegram_id",
        existing_type=sa.BigInteger(),
        nullable=True,
    )

    # Step 4: Update existing records to have user_type='telegram'
    # This is already done by server_default, but let's be explicit
    op.execute("UPDATE users SET user_type = 'telegram' WHERE user_type IS NULL")

    # Step 5: Add CHECK constraint for data consistency
    # Telegram users: telegram_id NOT NULL, password_hash IS NULL, role IS NULL
    # Web users: telegram_id IS NULL, password_hash NOT NULL, role NOT NULL
    op.create_check_constraint(
        "users_type_consistency_check",
        "users",
        """
        (user_type = 'telegram' AND telegram_id IS NOT NULL 
         AND password_hash IS NULL AND role IS NULL)
        OR
        (user_type = 'web' AND telegram_id IS NULL 
         AND password_hash IS NOT NULL AND role IS NOT NULL)
        """,
    )

    # Step 6: Create partial unique index on username for web users
    op.create_index(
        "ix_users_web_username_unique",
        "users",
        ["username"],
        unique=True,
        postgresql_where=sa.text("user_type = 'web'"),
    )

    # Step 7: Seed administrator account
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

    # Hash password with bcrypt
    password_hash = bcrypt.hashpw(admin_password.encode("utf-8"), bcrypt.gensalt(rounds=12))
    password_hash_str = password_hash.decode("utf-8")

    # Insert admin user
    op.execute(
        sa.text(
            """
        INSERT INTO users 
            (user_type, username, first_name, password_hash, role, is_active)
        VALUES 
            ('web', :username, 'Administrator', :password_hash, 'administrator', true)
        ON CONFLICT DO NOTHING
        """
        ).bindparams(
            username=admin_username,
            password_hash=password_hash_str,
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Delete web users (including the admin)
    op.execute("DELETE FROM users WHERE user_type = 'web'")

    # Drop index
    op.drop_index("ix_users_web_username_unique", table_name="users")

    # Drop CHECK constraint
    op.drop_constraint("users_type_consistency_check", "users", type_="check")

    # Drop columns
    op.drop_column("users", "last_login")
    op.drop_column("users", "role")
    op.drop_column("users", "password_hash")
    op.drop_column("users", "user_type")

    # Make telegram_id NOT NULL again
    op.alter_column(
        "users",
        "telegram_id",
        existing_type=sa.BigInteger(),
        nullable=False,
    )

    # Drop enum types
    sa.Enum(name="user_role_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="user_type_enum").drop(op.get_bind(), checkfirst=True)
