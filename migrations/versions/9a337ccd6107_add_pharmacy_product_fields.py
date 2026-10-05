"""add pharmacy product fields

Revision ID: 9a337ccd6107
Revises: 712a792a742c
Create Date: 2026-01-03 21:37:57.745570
"""

from alembic import op
import sqlalchemy as sa


revision = '9a337ccd6107'
down_revision = '712a792a742c'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.alter_column(
            'payment_status',
            existing_type=sa.VARCHAR(length=20),
            nullable=True,
            existing_server_default=sa.text("'pending'")
        )

    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('is_active', sa.Boolean(), nullable=True)
        )
        batch_op.add_column(
            sa.Column('batch_number', sa.String(length=100), nullable=True)
        )
        batch_op.add_column(
            sa.Column('expiry_date', sa.Date(), nullable=True)
        )
        batch_op.add_column(
            sa.Column('reorder_level', sa.Integer(), nullable=True)
        )
        batch_op.add_column(
            sa.Column('updated_at', sa.DateTime(), nullable=True)
        )


def downgrade():
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.drop_column('updated_at')
        batch_op.drop_column('reorder_level')
        batch_op.drop_column('expiry_date')
        batch_op.drop_column('batch_number')
        batch_op.drop_column('is_active')

    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.alter_column(
            'payment_status',
            existing_type=sa.VARCHAR(length=20),
            nullable=False,
            existing_server_default=sa.text("'pending'")
        )
