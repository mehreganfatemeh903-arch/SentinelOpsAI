"""agent tool permission bindings
Revision ID: 0002_agent_tool_bindings
Revises: 0001_initial
"""
from alembic import op
import sqlalchemy as sa
revision='0002_agent_tool_bindings'; down_revision='0001_initial'; branch_labels=None; depends_on=None

def upgrade():
    bind = op.get_bind()
    if sa.inspect(bind).has_table('agent_tools'):
        return
    op.create_table(
        'agent_tools',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('agent_id', sa.String(length=36), sa.ForeignKey('agents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tool_id', sa.String(length=36), sa.ForeignKey('tools.id', ondelete='CASCADE'), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('agent_id','tool_id',name='uq_agent_tool'),
    )
    op.create_index('ix_agent_tools_agent_id','agent_tools',['agent_id'])
    op.create_index('ix_agent_tools_tool_id','agent_tools',['tool_id'])

def downgrade():
    op.drop_index('ix_agent_tools_tool_id',table_name='agent_tools')
    op.drop_index('ix_agent_tools_agent_id',table_name='agent_tools')
    op.drop_table('agent_tools')
