"""Create materialized view mv_payments_by_method

Revision ID: e5f6g7h8i9j0
Revises: d4e5f6g7h8i9
Create Date: 2025-11-08 22:30:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = "e5f6g7h8i9j0"
down_revision: Union[str, Sequence[str], None] = "d4e5f6g7h8i9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create materialized view mv_payments_by_method"""
    op.execute("""
    CREATE MATERIALIZED VIEW mv_payments_by_method AS
    SELECT
        pay.method AS payment_method,
        COUNT(DISTINCT o.id) AS total_orders,
        SUM(oi.quantity) AS total_quantity,
        SUM(oi.total_cost) AS total_amount,
        SUM(pay.amount) AS total_payments
    FROM payments pay
    LEFT JOIN orders o ON o.id = pay.order_id
    LEFT JOIN order_items oi ON oi.order_id = o.id
    GROUP BY pay.method
    ORDER BY total_payments DESC;
    """)


def downgrade() -> None:
    """Drop materialized view mv_payments_by_method"""
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_payments_by_method;")
