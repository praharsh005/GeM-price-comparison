"""reconcile_schema_add_missing_columns_and_product_matches

Revision ID: 69d7c98c7133
Revises: 3f2a9c1d4e5b
Create Date: 2026-08-24 22:25:27.301129

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '69d7c98c7133'
down_revision: Union[str, Sequence[str], None] = '3f2a9c1d4e5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # marketplaces: add slug, logo_url, is_active, created_at
    op.add_column('marketplaces', sa.Column('slug', sa.String(50), unique=True, nullable=False, server_default=''))
    op.add_column('marketplaces', sa.Column('logo_url', sa.String(500), nullable=True))
    op.add_column('marketplaces', sa.Column('is_active', sa.Boolean(), default=True, nullable=False, server_default=sa.true()))
    op.add_column('marketplaces', sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))

    # products: add image_url, updated_at
    op.add_column('products', sa.Column('image_url', sa.String(500), nullable=True))
    op.add_column('products', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))

    # listings: add price (Numeric), availability_new (Boolean), last_checked_at
    op.add_column('listings', sa.Column('price', sa.Numeric(12, 2), nullable=True))
    op.add_column('listings', sa.Column('availability_new', sa.Boolean(), default=True, nullable=False))
    op.add_column('listings', sa.Column('last_checked_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))

    # Migrate data: current_price -> price
    op.execute('UPDATE listings SET price = current_price::numeric(12,2) WHERE current_price IS NOT NULL')

    # Migrate data: availability string -> boolean
    op.execute("""
        UPDATE listings 
        SET availability_new = CASE 
            WHEN lower(availability) IN ('in_stock', 'available', 'true', '1', 'yes') THEN true 
            ELSE false 
        END
    """)

    # Drop old columns
    op.drop_column('listings', 'current_price')
    op.drop_column('listings', 'availability')

    # Rename availability_new -> availability
    op.alter_column('listings', 'availability_new', new_column_name='availability')

    # product_matches table
    op.create_table(
        'product_matches',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('product_a_id', sa.Integer(), sa.ForeignKey('products.id', ondelete='CASCADE'), index=True, nullable=False),
        sa.Column('product_b_id', sa.Integer(), sa.ForeignKey('products.id', ondelete='CASCADE'), index=True, nullable=False),
        sa.Column('confidence', sa.Numeric(5, 2), nullable=False),
        sa.Column('method', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.UniqueConstraint('product_a_id', 'product_b_id', name='uq_match_pair'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('product_matches')

    # listings: add back current_price, restore availability as String
    op.add_column('listings', sa.Column('availability_old', sa.String(50), nullable=True))
    op.add_column('listings', sa.Column('current_price', sa.Float(), nullable=True))
    
    op.execute('UPDATE listings SET current_price = price::float WHERE price IS NOT NULL')
    op.execute("UPDATE listings SET availability_old = CASE WHEN availability THEN 'in_stock' ELSE 'out_of_stock' END")
    
    op.drop_column('listings', 'price')
    op.drop_column('listings', 'availability')
    op.drop_column('listings', 'last_checked_at')
    op.alter_column('listings', 'availability_old', new_column_name='availability')

    # products
    op.drop_column('products', 'updated_at')
    op.drop_column('products', 'image_url')

    # marketplaces
    op.drop_column('marketplaces', 'created_at')
    op.drop_column('marketplaces', 'is_active')
    op.drop_column('marketplaces', 'logo_url')
    op.drop_column('marketplaces', 'slug')