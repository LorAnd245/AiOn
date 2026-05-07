"""v2_new_tables

Revision ID: 001_v2_new_tables
Revises: 
Create Date: 2025-01-15 13:57:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '001_v2_new_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create audit_logs table
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('actor_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('detail', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_created_at'), 'audit_logs', ['created_at'], unique=False)
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)

    # Create usage_stats table
    op.create_table('usage_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('message_count', sa.Integer(), nullable=True),
        sa.Column('token_count', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('agent_id', 'user_id', 'date', name='uq_usage_stats_agent_user_date')
    )
    op.create_index(op.f('ix_usage_stats_agent_id'), 'usage_stats', ['agent_id'], unique=False)
    op.create_index(op.f('ix_usage_stats_date'), 'usage_stats', ['date'], unique=False)
    op.create_index(op.f('ix_usage_stats_id'), 'usage_stats', ['id'], unique=False)

    # Create refresh_tokens table
    op.create_table('refresh_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('token_hash', sa.String(length=64), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('revoked', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_hash')
    )
    op.create_index(op.f('ix_refresh_tokens_id'), 'refresh_tokens', ['id'], unique=False)
    op.create_index(op.f('ix_refresh_tokens_user_id'), 'refresh_tokens', ['user_id'], unique=False)

    # Add new columns to messages table
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.add_column(sa.Column('feedback', sa.String(length=4), nullable=True))
        batch_op.add_column(sa.Column('feedback_user_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('token_count', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_messages_feedback_user_id', 'users', ['feedback_user_id'], ['id'])


def downgrade() -> None:
    # Remove columns from messages table
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.drop_constraint('fk_messages_feedback_user_id', type_='foreignkey')
        batch_op.drop_column('token_count')
        batch_op.drop_column('feedback_user_id')
        batch_op.drop_column('feedback')

    # Drop refresh_tokens table
    op.drop_index(op.f('ix_refresh_tokens_user_id'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_id'), table_name='refresh_tokens')
    op.drop_table('refresh_tokens')

    # Drop usage_stats table
    op.drop_index(op.f('ix_usage_stats_id'), table_name='usage_stats')
    op.drop_index(op.f('ix_usage_stats_date'), table_name='usage_stats')
    op.drop_index(op.f('ix_usage_stats_agent_id'), table_name='usage_stats')
    op.drop_table('usage_stats')

    # Drop audit_logs table
    op.drop_index(op.f('ix_audit_logs_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_created_at'), table_name='audit_logs')
    op.drop_table('audit_logs')
