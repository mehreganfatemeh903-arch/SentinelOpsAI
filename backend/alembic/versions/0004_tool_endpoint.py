"""add tool endpoint

Revision ID: 0004_tool_endpoint
Revises: 0003_tool_adapter_credentials
"""

from alembic import op
import sqlalchemy as sa


revision = "0004_tool_endpoint"
down_revision = "0003_tool_adapter_credentials"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "tools",
        sa.Column(
            "endpoint",
            sa.String(length=500),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column("tools", "endpoint")
