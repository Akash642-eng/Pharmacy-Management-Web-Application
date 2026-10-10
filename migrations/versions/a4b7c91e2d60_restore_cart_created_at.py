
"""Restore created_at column on carts.

Revision ID: a4b7c91e2d60
Revises: 9a337ccd6107
"""

from alembic import op
import sqlalchemy as sa

revision = "a4b7c91e2d60"
down_revision = "9a337ccd6107"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "carts",
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_column("carts", "created_at")
