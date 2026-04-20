"""add payment and invoice fields to orders

Revision ID: 3e927f030fd9
Revises: dfbc5d475f80
Create Date: 2025-12-29
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3e927f030fd9"
down_revision = "dfbc5d475f80"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("orders", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("payment_method", sa.String(length=20), nullable=True)
        )
        batch_op.add_column(
            sa.Column(
                "payment_status",
                sa.String(length=20),
                nullable=False,
                server_default="pending",
            )
        )
        batch_op.add_column(
            sa.Column("invoice_number", sa.String(length=50), nullable=True)
        )

        # ✅ IMPORTANT: Named UNIQUE constraint (SQLite-safe)
        batch_op.create_unique_constraint(
            "uq_orders_invoice_number", ["invoice_number"]
        )


def downgrade():
    with op.batch_alter_table("orders", schema=None) as batch_op:
        batch_op.drop_constraint(
            "uq_orders_invoice_number", type_="unique"
        )
        batch_op.drop_column("invoice_number")
        batch_op.drop_column("payment_status")
        batch_op.drop_column("payment_method")
