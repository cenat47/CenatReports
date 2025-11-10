from datetime import datetime
from sqlalchemy import Numeric, Integer, Date
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base


class SalesDailyORM(Base):
    __tablename__ = "mv_sales_daily"

    date: Mapped[datetime] = mapped_column(Date, primary_key=True)
    total_orders: Mapped[int] = mapped_column(Integer)
    total_amount: Mapped[Numeric] = mapped_column(Numeric)
    avg_check: Mapped[Numeric] = mapped_column(Numeric)
    total_items: Mapped[int] = mapped_column(Integer)
    total_payments: Mapped[Numeric] = mapped_column(Numeric)
