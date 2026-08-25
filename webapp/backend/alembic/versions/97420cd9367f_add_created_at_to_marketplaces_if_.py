"""add_created_at_to_marketplaces_if_missing

Revision ID: 97420cd9367f
Revises: 69d7c98c7133
Create Date: 2026-08-25 22:14:20.742489

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '97420cd9367f'
down_revision: Union[str, Sequence[str], None] = '69d7c98c7133'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(conn, table: str, column: str) -> bool:
    result = conn.execute(
        text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_name = :table AND column_name = :column"
        ),
        {"table": table, "column": column},
    )
    return result.fetchone() is not None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()

    if not _column_exists(conn, "marketplaces", "created_at"):
        op.add_column(
            "marketplaces",
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
        )

    if not _column_exists(conn, "marketplaces", "slug"):
        op.add_column(
            "marketplaces",
            sa.Column("slug", sa.String(50), nullable=False, server_default=""),
        )

    if not _column_exists(conn, "marketplaces", "logo_url"):
        op.add_column(
            "marketplaces", sa.Column("logo_url", sa.String(500), nullable=True)
        )

    if not _column_exists(conn, "marketplaces", "is_active"):
        op.add_column(
            "marketplaces",
            sa.Column(
                "is_active",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            ),
        )

    if not _column_exists(conn, "products", "image_url"):
        op.add_column(
            "products", sa.Column("image_url", sa.String(500), nullable=True)
        )

    if not _column_exists(conn, "products", "updated_at"):
        op.add_column(
            "products",
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        )

    if not _column_exists(conn, "listings", "price"):
        op.add_column(
            "listings", sa.Column("price", sa.Numeric(12, 2), nullable=True)
        )

    if not _column_exists(conn, "listings", "last_checked_at"):
        op.add_column(
            "listings",
            sa.Column(
                "last_checked_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
        )

    # listings.availability must be boolean; fix type if it's not
    result = conn.execute(
        text(
            "SELECT data_type FROM information_schema.columns "
            "WHERE table_name = 'listings' AND column_name = 'availability'"
        )
    )
    row = result.fetchone()
    if row is not None and row[0] != "boolean":
        op.add_column(
            "listings",
            sa.Column(
                "availability_new",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            ),
        )
        op.execute(
            "UPDATE listings SET availability_new = CASE WHEN lower(availability) "
            "IN ('in_stock', 'available', 'true', '1', 'yes') THEN true ELSE false END"
        )
        op.drop_column("listings", "availability")
        op.alter_column(
            "listings", "availability_new", new_column_name="availability"
        )

    # Drop legacy current_price if both it and price exist
    if _column_exists(conn, "listings", "current_price") and _column_exists(
        conn, "listings", "price"
    ):
        op.execute(
            "UPDATE listings SET price = current_price "
            "WHERE current_price IS NOT NULL AND price IS NULL"
        )
        op.drop_column("listings", "current_price")

    # product_matches table
    conn.execute(
        text(
            "CREATE TABLE IF NOT EXISTS product_matches ("
            "id SERIAL PRIMARY KEY, "
            "product_a_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE, "
            "product_b_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE, "
            "confidence NUMERIC(5, 2) NOT NULL, "
            "method VARCHAR(50) NOT NULL, "
            "created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, "
            "CONSTRAINT uq_match_pair UNIQUE (product_a_id, product_b_id))"
        )
    )
    conn.execute(
        text(
            "CREATE INDEX IF NOT EXISTS ix_product_matches_product_a_id "
            "ON product_matches (product_a_id)"
        )
    )
    conn.execute(
        text(
            "CREATE INDEX IF NOT EXISTS ix_product_matches_product_b_id "
            "ON product_matches (product_b_id)"
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
