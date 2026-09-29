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
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("tools")}

    if "adapter_name" not in columns:
        op.add_column(
            "tools",
            sa.Column(
                "adapter_name",
                sa.String(length=80),
                nullable=False,
                server_default="simulated",
            ),
        )

    if "credential_ref" not in columns:
        op.add_column(
            "tools",
            sa.Column(
                "credential_ref",
                sa.String(length=120),
                nullable=True,
            ),
        )

    if "adapter_name" in columns or "adapter_name" in {
        column["name"] for column in sa.inspect(bind).get_columns("tools")
    }:
        op.alter_column(
            "tools",
            "adapter_name",
            server_default=None,
        )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("tools")}

    if "credential_ref" in columns:
        op.drop_column("tools", "credential_ref")

    if "adapter_name" in columns:
        op.drop_column("tools", "adapter_name")