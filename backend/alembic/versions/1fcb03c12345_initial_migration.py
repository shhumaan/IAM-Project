"""Initial migration.

Revision ID: 1fcb03c12345
Revises: 
Create Date: 2023-04-01 12:00:00

"""
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1fcb03c12345'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create user table
    op.create_table(
        'user',
        sa.Column('id', sa.String(36), primary_key=True, default=lambda: str(uuid4())),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(255), nullable=True),
        sa.Column('last_name', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, default=False),
        sa.Column('mfa_enabled', sa.Boolean(), nullable=False, default=False),
        sa.Column('mfa_secret', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create role table
    op.create_table(
        'role',
        sa.Column('id', sa.String(36), primary_key=True, default=lambda: str(uuid4())),
        sa.Column('name', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create policy table
    op.create_table(
        'policy',
        sa.Column('id', sa.String(36), primary_key=True, default=lambda: str(uuid4())),
        sa.Column('name', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('effect', sa.String(50), nullable=False),
        sa.Column('actions', postgresql.JSONB, nullable=False),
        sa.Column('resources', postgresql.JSONB, nullable=False),
        sa.Column('conditions', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create attribute_definition table
    op.create_table(
        'attribute_definition',
        sa.Column('id', sa.String(36), primary_key=True, default=lambda: str(uuid4())),
        sa.Column('name', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('data_type', sa.String(50), nullable=False),
        sa.Column('is_required', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_multivalued', sa.Boolean(), nullable=False, default=False),
        sa.Column('default_value', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create attribute_value table
    op.create_table(
        'attribute_value',
        sa.Column('id', sa.String(36), primary_key=True, default=lambda: str(uuid4())),
        sa.Column('attribute_def_id', sa.String(36), sa.ForeignKey('attribute_definition.id'), nullable=False, index=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('user.id'), nullable=True, index=True),
        sa.Column('value', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create user_role association table
    op.create_table(
        'user_role',
        sa.Column('user_id', sa.String(36), sa.ForeignKey('user.id'), primary_key=True),
        sa.Column('role_id', sa.String(36), sa.ForeignKey('role.id'), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # Create role_policy association table
    op.create_table(
        'role_policy',
        sa.Column('role_id', sa.String(36), sa.ForeignKey('role.id'), primary_key=True),
        sa.Column('policy_id', sa.String(36), sa.ForeignKey('policy.id'), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # Create access_log table
    op.create_table(
        'access_log',
        sa.Column('id', sa.String(36), primary_key=True, default=lambda: str(uuid4())),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('user.id'), nullable=True, index=True),
        sa.Column('resource_id', sa.String(255), nullable=False, index=True),
        sa.Column('resource_type', sa.String(50), nullable=False, index=True),
        sa.Column('action', sa.String(50), nullable=False, index=True),
        sa.Column('status', sa.String(50), nullable=False, index=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('user_agent', sa.String(255), nullable=True),
        sa.Column('details', postgresql.JSONB, nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, index=True),
    )
    
    # Create audit_log table
    op.create_table(
        'audit_log',
        sa.Column('id', sa.String(36), primary_key=True, default=lambda: str(uuid4())),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('user.id'), nullable=True, index=True),
        sa.Column('entity_id', sa.String(255), nullable=False, index=True),
        sa.Column('entity_type', sa.String(50), nullable=False, index=True),
        sa.Column('action', sa.String(50), nullable=False, index=True),
        sa.Column('previous_state', postgresql.JSONB, nullable=True),
        sa.Column('new_state', postgresql.JSONB, nullable=True),
        sa.Column('details', postgresql.JSONB, nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, index=True),
    )


def downgrade():
    op.drop_table('audit_log')
    op.drop_table('access_log')
    op.drop_table('role_policy')
    op.drop_table('user_role')
    op.drop_table('attribute_value')
    op.drop_table('attribute_definition')
    op.drop_table('policy')
    op.drop_table('role')
    op.drop_table('user') 