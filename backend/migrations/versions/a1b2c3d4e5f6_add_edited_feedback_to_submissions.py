"""Add edited_feedback column to submissions for professor corrections.

Revision ID: a1b2c3d4e5f6
Revises: 3e1145558b32
Create Date: 2026-02-09
"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = '3e1145558b32'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('submissions', sa.Column('edited_feedback', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('submissions', 'edited_feedback')
