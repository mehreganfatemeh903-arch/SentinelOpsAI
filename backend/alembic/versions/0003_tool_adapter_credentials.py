"""add tool adapter and credential reference

Revision ID: 0003_tool_adapter_credentials
Revises: 0002_agent_tool_bindings
"""

from alembic import op
import sqlalchemy as sa


revision = "0003_tool_adapter_credentials"
down_revision = "0002_agent_tool_bindings"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "tools",
        sa.Column(
            "adapter_name",
            sa.String(length=80),
            nullable=False,
            server_default="simulated",
        ),
    )

    op.add_column(
        "tools",
        sa.Column(
            "credential_ref",
            sa.String(length=120),
            nullable=True,
        ),
    )

    op.alter_column(
        "tools",
        "adapter_name",
        server_default=None,
    )


def downgrade():
    op.drop_column("tools", "credential_ref")
    op.drop_column("tools", "adapter_name")
