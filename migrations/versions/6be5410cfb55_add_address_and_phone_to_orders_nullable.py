"""Add address and phone to orders (nullable)

Revision ID: 6be5410cfb55
Revises: 4a637b9db2ba
Create Date: 2025-12-29 11:47:57.455071
"""

from alembic import op
import sqlalchemy as sa


revision = '6be5410cfb55'
down_revision = '4a637b9db2ba'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('address', sa.Text(), nullable=True)
        )
        batch_op.add_column(
            sa.Column('phone', sa.String(length=15), nullable=True)
        )
        batch_op.alter_column(
            'status',
            existing_type=sa.VARCHAR(length=50),
            type_=sa.String(length=30),
            existing_nullable=True
        )


def downgrade():
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.alter_column(
            'status',
            existing_type=sa.String(length=30),
            type_=sa.VARCHAR(length=50),
            existing_nullable=True
        )
        batch_op.drop_column('phone')
        batch_op.drop_column('address')
