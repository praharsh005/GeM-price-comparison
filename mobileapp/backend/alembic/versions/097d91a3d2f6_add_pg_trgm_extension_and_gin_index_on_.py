"""add pg_trgm extension and GIN index on product name

Revision ID: 097d91a3d2f6
Revises: b1b82de1515c
Create Date: 2026-08-18 23:17:37.107890

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '097d91a3d2f6'
down_revision: Union[str, Sequence[str], None] = 'b1b82de1515c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute(
        "CREATE INDEX ix_products_name_trgm ON products USING gin (name gin_trgm_ops)"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX IF EXISTS ix_products_name_trgm")
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
