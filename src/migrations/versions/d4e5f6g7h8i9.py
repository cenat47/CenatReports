"""Create materialized view mv_sales_by_customer

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2025-11-08 22:00:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = "d4e5f6g7h8i9"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f6g7h8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create materialized view mv_sales_by_customer"""
    op.execute("""
    CREATE MATERIALIZED VIEW mv_sales_by_customer AS
    WITH payments_agg AS (
        SELECT order_id, SUM(amount) AS total_payments
        FROM payments
        GROUP BY order_id
    )
    SELECT
        cu.id AS customer_id,
        cu.name AS customer_name,
        cu.email AS customer_email,
        SUM(oi.quantity) AS total_quantity,
        SUM(oi.total_cost) AS total_amount,
        COUNT(DISTINCT o.id) AS total_orders,
        SUM(COALESCE(pay.total_payments, 0)) AS total_payments
    FROM customers cu
    LEFT JOIN orders o ON o.customer_id = cu.id
    LEFT JOIN order_items oi ON oi.order_id = o.id
    LEFT JOIN payments_agg pay ON pay.order_id = o.id
    GROUP BY cu.id, cu.name, cu.email
    ORDER BY total_amount DESC;
    """)


def downgrade() -> None:
    """Drop materialized view mv_sales_by_customer"""
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_sales_by_customer;")
