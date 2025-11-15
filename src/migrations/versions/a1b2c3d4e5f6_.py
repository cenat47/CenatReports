"""Create materialized view mv_sales_daily

Revision ID: a1b2c3d4e5f6
Revises: cf61916f159d
Create Date: 2025-11-08 17:33:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "cf61916f159d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create materialized view mv_sales_daily"""
    op.execute("""
        CREATE MATERIALIZED VIEW mv_sales_daily AS
    WITH payments_agg AS (
        SELECT order_id, SUM(amount) AS total_payments
        FROM payments
        GROUP BY order_id
    ),
    items_agg AS (
        SELECT order_id,
            SUM(quantity) AS total_items
        FROM order_items
        GROUP BY order_id
    )
    SELECT
        o.order_date::date AS date,
        COUNT(*) AS total_orders,
        SUM(o.total_amount) AS total_amount,
        AVG(o.total_amount) AS avg_check,
        SUM(COALESCE(i.total_items, 0)) AS total_items,
        SUM(COALESCE(p.total_payments, 0)) AS total_payments
    FROM orders o
    LEFT JOIN items_agg i ON i.order_id = o.id
    LEFT JOIN payments_agg p ON p.order_id = o.id
    GROUP BY o.order_date::date
    ORDER BY o.order_date::date;

    """)


def downgrade() -> None:
    """Drop materialized view mv_sales_daily"""
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_sales_daily;")
