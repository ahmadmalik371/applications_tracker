"""Add rules and rule_evaluations tables

Revision ID: 7c2d8f9e3a1b
Revises: 5b9a87680ce9
Create Date: 2026-07-18 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c2d8f9e3a1b'
down_revision: Union[str, Sequence[str], None] = '5b9a87680ce9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'rules',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('rule_type', sa.String(length=50), nullable=False),
        sa.Column('operator', sa.String(length=50), nullable=False),
        sa.Column('condition_value', sa.JSON(), nullable=False),
        sa.Column('score_impact', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('is_blocking', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('priority', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by_id', sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_rules_organization_id'), 'rules', ['organization_id'], unique=False)
    op.create_index(op.f('ix_rules_created_by_id'), 'rules', ['created_by_id'], unique=False)

    op.create_table(
        'rule_evaluations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('rule_id', sa.UUID(), nullable=False),
        sa.Column('candidate_id', sa.UUID(), nullable=False),
        sa.Column('job_id', sa.UUID(), nullable=False),
        sa.Column('passed', sa.Boolean(), nullable=False),
        sa.Column('reason', sa.String(length=500), nullable=True),
        sa.Column('score_impact', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('evaluated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['rule_id'], ['rules.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_rule_evaluations_rule_id'), 'rule_evaluations', ['rule_id'], unique=False)
    op.create_index(op.f('ix_rule_evaluations_candidate_id'), 'rule_evaluations', ['candidate_id'], unique=False)
    op.create_index(op.f('ix_rule_evaluations_job_id'), 'rule_evaluations', ['job_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_rule_evaluations_job_id'), table_name='rule_evaluations')
    op.drop_index(op.f('ix_rule_evaluations_candidate_id'), table_name='rule_evaluations')
    op.drop_index(op.f('ix_rule_evaluations_rule_id'), table_name='rule_evaluations')
    op.drop_table('rule_evaluations')
    op.drop_index(op.f('ix_rules_created_by_id'), table_name='rules')
    op.drop_index(op.f('ix_rules_organization_id'), table_name='rules')
    op.drop_table('rules')
