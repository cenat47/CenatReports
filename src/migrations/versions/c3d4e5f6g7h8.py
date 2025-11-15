"""Create materialized view mv_sales_by_category

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2025-11-08 21:30:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = "c3d4e5f6g7h8"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6g7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create materialized view mv_sales_by_category"""
    op.execute("""
    CREATE MATERIALIZED VIEW mv_sales_by_category AS
    WITH payments_agg AS (
        SELECT order_id, SUM(amount) AS total_payments
        FROM payments
        GROUP BY order_id
    )
    SELECT
        c.id AS category_id,
        c.name AS category_name,
        SUM(oi.quantity) AS total_quantity,
        SUM(oi.total_cost) AS total_amount,
        COUNT(DISTINCT o.id) AS total_orders,
        SUM(COALESCE(pay.total_payments, 0)) AS total_payments
    FROM categories c
    LEFT JOIN products p ON p.category_id = c.id
    LEFT JOIN order_items oi ON oi.product_id = p.id
    LEFT JOIN orders o ON o.id = oi.order_id
    LEFT JOIN payments_agg pay ON pay.order_id = o.id
    GROUP BY c.id, c.name
    ORDER BY total_amount DESC;

    """)


def downgrade() -> None:
    """Drop materialized view mv_sales_by_category"""
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_sales_by_category;")
