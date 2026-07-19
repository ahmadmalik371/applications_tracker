"""Add super admin, audit, activity, and AI ML tables

Revision ID: a1b2c3d4e5f6
Revises: 8d3e9f0a4b2c
Create Date: 2026-07-19 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '8d3e9f0a4b2c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # SaaS Plans
    op.create_table(
        'saas_plans',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('tier', sa.String(length=50), nullable=False, server_default='Free'),
        sa.Column('price_cents', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('billing_cycle', sa.String(length=20), nullable=False, server_default='monthly'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('max_users', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('max_resume_processing', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('max_ai_requests', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('max_storage_mb', sa.Integer(), nullable=False, server_default='500'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('stripe_price_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uix_saas_plans_name'),
    )
    op.create_index(op.f('ix_saas_plans_name'), 'saas_plans', ['name'], unique=True)

    # Subscriptions
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('plan_id', sa.UUID(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Active'),
        sa.Column('current_period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('trial_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('canceled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('usage_users', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('usage_resume_processing', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('usage_ai_requests', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('usage_storage_mb', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_customer_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['plan_id'], ['saas_plans.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_subscriptions_organization_id'), 'subscriptions', ['organization_id'])
    op.create_index(op.f('ix_subscriptions_plan_id'), 'subscriptions', ['plan_id'])

    # Feature Flags
    op.create_table(
        'feature_flags',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('module', sa.String(length=50), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('is_system', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key', name='uix_feature_flags_key'),
    )
    op.create_index(op.f('ix_feature_flags_key'), 'feature_flags', ['key'], unique=True)

    # Org Feature Flag Overrides
    op.create_table(
        'org_feature_flag_overrides',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('feature_flag_id', sa.UUID(), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['feature_flag_id'], ['feature_flags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'feature_flag_id', name='uix_org_flag_override'),
    )
    op.create_index(op.f('ix_org_feature_flag_overrides_organization_id'), 'org_feature_flag_overrides', ['organization_id'])
    op.create_index(op.f('ix_org_feature_flag_overrides_feature_flag_id'), 'org_feature_flag_overrides', ['feature_flag_id'])

    # Platform Settings
    op.create_table(
        'platform_settings',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', postgresql.JSONB(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key', name='uix_platform_settings_key'),
    )
    op.create_index(op.f('ix_platform_settings_key'), 'platform_settings', ['key'], unique=True)

    # System Announcements
    op.create_table(
        'system_announcements',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False, server_default='info'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('starts_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ends_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # Global Roles
    op.create_table(
        'global_roles',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('permissions', postgresql.JSONB(), nullable=True),
        sa.Column('is_system', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uix_global_roles_name'),
    )
    op.create_index(op.f('ix_global_roles_name'), 'global_roles', ['name'], unique=True)

    # Audit Logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('organization_id', sa.UUID(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', sa.String(length=64), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'])
    op.create_index(op.f('ix_audit_logs_organization_id'), 'audit_logs', ['organization_id'])
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'])
    op.create_index(op.f('ix_audit_logs_resource_type'), 'audit_logs', ['resource_type'])
    op.create_index(op.f('ix_audit_logs_occurred_at'), 'audit_logs', ['occurred_at'])

    # Activity Timeline
    op.create_table(
        'activity_timeline',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=True),
        sa.Column('actor_id', sa.UUID(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('summary', sa.String(length=500), nullable=True),
        sa.Column('details', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_activity_timeline_entity_type'), 'activity_timeline', ['entity_type'])
    op.create_index(op.f('ix_activity_timeline_entity_id'), 'activity_timeline', ['entity_id'])
    op.create_index(op.f('ix_activity_timeline_organization_id'), 'activity_timeline', ['organization_id'])
    op.create_index(op.f('ix_activity_timeline_actor_id'), 'activity_timeline', ['actor_id'])

    # AI Recommendation Feedback
    op.create_table(
        'ai_recommendation_feedback',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('recruiter_id', sa.UUID(), nullable=True),
        sa.Column('candidate_id', sa.UUID(), nullable=True),
        sa.Column('job_id', sa.UUID(), nullable=True),
        sa.Column('ranking_score', sa.Float(), nullable=True),
        sa.Column('rating', sa.String(length=50), nullable=False),
        sa.Column('note', sa.String(length=500), nullable=True),
        sa.Column('context', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recruiter_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_ai_recommendation_feedback_organization_id'), 'ai_recommendation_feedback', ['organization_id'])
    op.create_index(op.f('ix_ai_recommendation_feedback_recruiter_id'), 'ai_recommendation_feedback', ['recruiter_id'])

    # Model Versions
    op.create_table(
        'model_versions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('trained_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deployed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('metrics', postgresql.JSONB(), nullable=True),
        sa.Column('config', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_model_versions_name'), 'model_versions', ['name'])

    # Model Evaluations
    op.create_table(
        'model_evaluations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('model_version_id', sa.UUID(), nullable=False),
        sa.Column('precision', sa.Float(), nullable=True),
        sa.Column('recall', sa.Float(), nullable=True),
        sa.Column('f1', sa.Float(), nullable=True),
        sa.Column('roc_auc', sa.Float(), nullable=True),
        sa.Column('map_at_k', sa.Float(), nullable=True),
        sa.Column('ndcg', sa.Float(), nullable=True),
        sa.Column('latency_ms', sa.Float(), nullable=True),
        sa.Column('notes', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['model_version_id'], ['model_versions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_model_evaluations_model_version_id'), 'model_evaluations', ['model_version_id'])

    # Bias Reports
    op.create_table(
        'bias_reports',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=True),
        sa.Column('model_version_id', sa.UUID(), nullable=True),
        sa.Column('metric_type', sa.String(length=50), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=True),
        sa.Column('group_a', sa.String(length=100), nullable=True),
        sa.Column('group_b', sa.String(length=100), nullable=True),
        sa.Column('threshold', sa.Float(), nullable=True),
        sa.Column('is_flagged', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('details', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['model_version_id'], ['model_versions.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_bias_reports_organization_id'), 'bias_reports', ['organization_id'])
    op.create_index(op.f('ix_bias_reports_model_version_id'), 'bias_reports', ['model_version_id'])

    # Seed default feature flags
    op.execute("""
        INSERT INTO feature_flags (id, key, name, description, module, is_enabled, is_system)
        VALUES
            (gen_random_uuid(), 'ai_assistant', 'AI Assistant', 'Enable AI assistant capabilities', 'ai', true, true),
            (gen_random_uuid(), 'resume_parsing', 'Resume Parsing', 'Enable resume parsing', 'resume', true, true),
            (gen_random_uuid(), 'semantic_search', 'Semantic Search', 'Enable semantic search', 'search', true, true),
            (gen_random_uuid(), 'analytics', 'Analytics', 'Enable analytics module', 'analytics', true, true),
            (gen_random_uuid(), 'reporting', 'Reporting', 'Enable reporting module', 'reporting', true, true),
            (gen_random_uuid(), 'notifications', 'Notifications', 'Enable notifications module', 'notifications', true, true)
        ON CONFLICT (key) DO NOTHING;
    """)

    # Seed default SaaS plans
    op.execute("""
        INSERT INTO saas_plans (id, name, tier, price_cents, billing_cycle, is_active, max_users, max_resume_processing, max_ai_requests, max_storage_mb, description)
        VALUES
            (gen_random_uuid(), 'Free', 'Free', 0, 'monthly', true, 5, 50, 100, 500, 'Free tier with basic features'),
            (gen_random_uuid(), 'Professional', 'Professional', 4900, 'monthly', true, 50, 500, 5000, 5000, 'Professional tier with advanced features'),
            (gen_random_uuid(), 'Enterprise', 'Enterprise', 19900, 'monthly', true, 500, 5000, 50000, 50000, 'Enterprise tier with full features')
        ON CONFLICT (name) DO NOTHING;
    """)

    # Search optimization indexes (Task 18)
    op.execute("CREATE INDEX IF NOT EXISTS ix_candidates_embedding ON candidates USING ivfflat (embedded vector_cosine_ops) WITH (lists = 100);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_jobs_embedding ON jobs USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_candidates_tsv ON candidates USING gin (to_tsvector('english', coalesce(first_name,'') || ' ' || coalesce(last_name,'') || ' ' || email));")
    op.execute("CREATE INDEX IF NOT EXISTS ix_jobs_tsv ON jobs USING gin (to_tsvector('english', coalesce(title,'') || ' ' || coalesce(description,'')));")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX IF EXISTS ix_jobs_tsv;")
    op.execute("DROP INDEX IF EXISTS ix_candidates_tsv;")
    op.execute("DROP INDEX IF EXISTS ix_jobs_embedding;")
    op.execute("DROP INDEX IF EXISTS ix_candidates_embedding;")

    op.drop_index(op.f('ix_bias_reports_model_version_id'), table_name='bias_reports')
    op.drop_index(op.f('ix_bias_reports_organization_id'), table_name='bias_reports')
    op.drop_table('bias_reports')

    op.drop_index(op.f('ix_model_evaluations_model_version_id'), table_name='model_evaluations')
    op.drop_table('model_evaluations')

    op.drop_index(op.f('ix_model_versions_name'), table_name='model_versions')
    op.drop_table('model_versions')

    op.drop_index(op.f('ix_ai_recommendation_feedback_recruiter_id'), table_name='ai_recommendation_feedback')
    op.drop_index(op.f('ix_ai_recommendation_feedback_organization_id'), table_name='ai_recommendation_feedback')
    op.drop_table('ai_recommendation_feedback')

    op.drop_index(op.f('ix_activity_timeline_actor_id'), table_name='activity_timeline')
    op.drop_index(op.f('ix_activity_timeline_organization_id'), table_name='activity_timeline')
    op.drop_index(op.f('ix_activity_timeline_entity_id'), table_name='activity_timeline')
    op.drop_index(op.f('ix_activity_timeline_entity_type'), table_name='activity_timeline')
    op.drop_table('activity_timeline')

    op.drop_index(op.f('ix_audit_logs_occurred_at'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_resource_type'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_action'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_organization_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_table('audit_logs')

    op.drop_index(op.f('ix_global_roles_name'), table_name='global_roles')
    op.drop_table('global_roles')

    op.drop_table('system_announcements')

    op.drop_index(op.f('ix_platform_settings_key'), table_name='platform_settings')
    op.drop_table('platform_settings')

    op.drop_index(op.f('ix_org_feature_flag_overrides_feature_flag_id'), table_name='org_feature_flag_overrides')
    op.drop_index(op.f('ix_org_feature_flag_overrides_organization_id'), table_name='org_feature_flag_overrides')
    op.drop_table('org_feature_flag_overrides')

    op.drop_index(op.f('ix_feature_flags_key'), table_name='feature_flags')
    op.drop_table('feature_flags')

    op.drop_index(op.f('ix_subscriptions_plan_id'), table_name='subscriptions')
    op.drop_index(op.f('ix_subscriptions_organization_id'), table_name='subscriptions')
    op.drop_table('subscriptions')

    op.drop_index(op.f('ix_saas_plans_name'), table_name='saas_plans')
    op.drop_table('saas_plans')
