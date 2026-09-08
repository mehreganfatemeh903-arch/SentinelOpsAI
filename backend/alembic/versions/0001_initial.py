"""bootstrap schema
Revision ID: 0001_initial
Revises:
"""
from alembic import op
import app.models  # noqa: F401
from app.db.session import Base
revision='0001_initial'; down_revision=None; branch_labels=None; depends_on=None

def upgrade():
    # Bootstrap every ORM table so a clean database can be migrated from zero.
    Base.metadata.create_all(bind=op.get_bind())

def downgrade():
    Base.metadata.drop_all(bind=op.get_bind())
