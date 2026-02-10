"""Add prompt_test_runs table.

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-02-10 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'prompt_test_runs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('assignment_id', sa.Integer(), sa.ForeignKey('assignments.id'), nullable=False),
        sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('run_type', sa.String(20), nullable=False),
        sa.Column('label', sa.String(200)),
        sa.Column('code_analysis_prompt', sa.Text()),
        sa.Column('feedback_prompt', sa.Text()),
        sa.Column('comparison_code_analysis_prompt', sa.Text()),
        sa.Column('comparison_feedback_prompt', sa.Text()),
        sa.Column('submission_ids', sa.JSON()),
        sa.Column('results', sa.JSON()),
        sa.Column('status', sa.String(20), server_default='pending'),
        sa.Column('error_message', sa.Text()),
        sa.Column('total_duration_seconds', sa.Float()),
        sa.Column('grading_stats', sa.JSON()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime()),
    )


def downgrade():
    op.drop_table('prompt_test_runs')
