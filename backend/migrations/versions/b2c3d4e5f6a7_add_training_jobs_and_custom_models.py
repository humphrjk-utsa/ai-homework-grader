"""Add training_jobs and custom_models tables.

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-10
"""
from alembic import op
import sqlalchemy as sa

revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'training_jobs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('course_id', sa.Integer(), sa.ForeignKey('courses.id'), nullable=False),
        sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('base_model', sa.String(200), nullable=False),
        sa.Column('training_config', sa.JSON()),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('progress_percent', sa.Float(), server_default='0'),
        sa.Column('output_model_path', sa.String(500)),
        sa.Column('training_metrics', sa.JSON()),
        sa.Column('training_samples', sa.Integer(), server_default='0'),
        sa.Column('error_message', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('started_at', sa.DateTime()),
        sa.Column('completed_at', sa.DateTime()),
    )

    op.create_table(
        'custom_models',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('course_id', sa.Integer(), sa.ForeignKey('courses.id')),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('model_id', sa.String(500), nullable=False),
        sa.Column('model_type', sa.String(20), nullable=False, server_default='base'),
        sa.Column('server_url', sa.String(500)),
        sa.Column('container_id', sa.String(100)),
        sa.Column('status', sa.String(20), nullable=False, server_default='available'),
        sa.Column('deployment_config', sa.JSON()),
        sa.Column('training_job_id', sa.Integer(), sa.ForeignKey('training_jobs.id')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table('custom_models')
    op.drop_table('training_jobs')
