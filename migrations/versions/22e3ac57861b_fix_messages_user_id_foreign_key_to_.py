"""fix messages user_id foreign key to users.id

Revision ID: 22e3ac57861b
Revises: be090744c080
Create Date: 2025-10-17 21:42:31.274141

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "22e3ac57861b"
down_revision: Union[str, Sequence[str], None] = "be090744c080"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix foreign key in messages table to point to users.id instead of users.telegram_id."""
    # Drop old foreign key constraint
    op.drop_constraint("messages_user_id_fkey", "messages", type_="foreignkey")

    # Clean up old messages that reference telegram_id
    # We need to update user_id to reference users.id instead of telegram_id
    op.execute("""
        UPDATE messages m
        SET user_id = u.id
        FROM users u
        WHERE m.user_id = u.telegram_id AND u.telegram_id IS NOT NULL
    """)

    # Delete orphaned messages (where user_id doesn't match any users.id)
    op.execute("""
        DELETE FROM messages
        WHERE user_id NOT IN (SELECT id FROM users)
    """)

    # Create new foreign key constraint pointing to users.id
    op.create_foreign_key(
        "messages_user_id_fkey", "messages", "users", ["user_id"], ["id"], ondelete="CASCADE"
    )


def downgrade() -> None:
    """Revert foreign key in messages table to point to users.telegram_id."""
    # Drop new foreign key constraint
    op.drop_constraint("messages_user_id_fkey", "messages", type_="foreignkey")

    # Recreate old foreign key constraint pointing to users.telegram_id
    op.create_foreign_key(
        "messages_user_id_fkey",
        "messages",
        "users",
        ["user_id"],
        ["telegram_id"],
        ondelete="CASCADE",
    )
