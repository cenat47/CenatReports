"""Create materialized view mv_sales_by_product

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2025-11-08 21:00:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = "b2c3d4e5f6g7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create materialized view mv_sales_by_product"""
    op.execute("""
    CREATE MATERIALIZED VIEW mv_sales_by_product AS
    SELECT
        p.id AS product_id,
        p.name AS product_name,
        c.name AS category_name,
        SUM(oi.quantity) AS total_quantity,
        SUM(oi.total_cost) AS total_amount,
        COUNT(DISTINCT o.id) AS total_orders,
        COALESCE(SUM(pay.amount), 0) AS total_payments
    FROM products p
    LEFT JOIN order_items oi ON oi.product_id = p.id
    LEFT JOIN orders o ON o.id = oi.order_id
    LEFT JOIN payments pay ON pay.order_id = o.id
    LEFT JOIN categories c ON c.id = p.category_id
    GROUP BY p.id, p.name, c.name
    ORDER BY total_amount DESC;
    """)


def downgrade() -> None:
    """Drop materialized view mv_sales_by_product"""
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_sales_by_product;")
