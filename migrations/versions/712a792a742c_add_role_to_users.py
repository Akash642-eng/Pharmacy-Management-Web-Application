"""add role to users

Revision ID: 712a792a742c
Revises: 3e927f030fd9
Create Date: 2025-12-30
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '712a792a742c'
down_revision = '3e927f030fd9'
branch_labels = None
depends_on = None


def upgrade():
    # 1️⃣ Add column as NULLABLE (SQLite safe)
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(
            sa.Column('role', sa.String(length=20), nullable=True)
        )

    # 2️⃣ Backfill existing users
    op.execute("UPDATE users SET role = 'user' WHERE role IS NULL")

    # 3️⃣ Enforce NOT NULL (safe now)
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column(
            'role',
            existing_type=sa.String(length=20),
            nullable=False
        )


def downgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('role')
