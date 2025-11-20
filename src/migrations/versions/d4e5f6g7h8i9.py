"""Create materialized view mv_sales_by_customer

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2025-11-08 22:00:00.000000
"""

from typing import Sequence, Union
from alembic import op

# revision identifiers
revision: str = "d4e5f6g7h8i9"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f6g7h8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create materialized view mv_sales_by_customer"""
    op.execute("""
    CREATE MATERIALIZED VIEW mv_sales_by_customer_daily AS
    SELECT
        o.order_date::date AS order_date,
        cu.id AS customer_id,
        cu.name AS customer_name,
        cu.email AS customer_email,
        SUM(oi.quantity) AS total_quantity,
        SUM(oi.total_cost) AS total_amount,
        COUNT(DISTINCT o.id) AS total_orders,
        COALESCE(SUM(pay.amount), 0) AS total_payments
    FROM orders o
    JOIN customers cu ON o.customer_id = cu.id
    JOIN order_items oi ON oi.order_id = o.id
    LEFT JOIN payments pay ON pay.order_id = o.id
    GROUP BY o.order_date::date, cu.id, cu.name, cu.email;

    """)


def downgrade() -> None:
    """Drop materialized view mv_sales_by_customer"""
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_sales_by_customer;")
