"""Create materialized view mv_sales_by_product

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2025-11-08 21:00:00.000000
"""

from typing import Sequence, Union
from alembic import op

# revision identifiers
revision: str = "b2c3d4e5f6g7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create materialized view mv_sales_by_product_category_daily"""
    op.execute("""
    CREATE MATERIALIZED VIEW mv_sales_by_product_category_daily AS
    SELECT
        o.order_date::date AS order_date,
        p.id AS product_id,
        p.name AS product_name,
        c.id AS category_id,
        c.name AS category_name,
        SUM(oi.quantity) AS total_quantity,
        SUM(oi.total_cost) AS total_amount,
        COUNT(DISTINCT o.id) AS total_orders,
        COALESCE(SUM(pay.amount), 0) AS total_payments
    FROM order_items oi
    JOIN products p ON oi.product_id = p.id
    JOIN categories c ON p.category_id = c.id
    JOIN orders o ON oi.order_id = o.id
    LEFT JOIN payments pay ON pay.order_id = o.id
    GROUP BY o.order_date::date, p.id, p.name, c.id, c.name;


    """)


def downgrade() -> None:
    """Drop materialized view mv_sales_by_product"""
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_sales_by_product;")
