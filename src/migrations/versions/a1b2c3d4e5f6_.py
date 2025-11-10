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
    SELECT
        o.order_date::date AS date,
        COUNT(DISTINCT o.id) AS total_orders,
        SUM(o.total_amount) AS total_amount,
        AVG(o.total_amount) AS avg_check,
        SUM(oi.quantity) AS total_items,
        COALESCE(SUM(p.amount), 0) AS total_payments
    FROM orders o
    LEFT JOIN order_items oi ON oi.order_id = o.id
    LEFT JOIN payments p ON p.order_id = o.id
    GROUP BY o.order_date::date
    ORDER BY o.order_date::date;
    """)


def downgrade() -> None:
    """Drop materialized view mv_sales_daily"""
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_sales_daily;")
