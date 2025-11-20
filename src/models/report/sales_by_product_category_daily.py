from sqlalchemy import Date, String, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base
from datetime import datetime


class SalesByProductCategoryDailyORM(Base):
    __tablename__ = "mv_sales_by_product_category_daily"

    order_date: Mapped[datetime] = mapped_column(Date, primary_key=True)

    product_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_name: Mapped[str] = mapped_column(String(255))

    category_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category_name: Mapped[str] = mapped_column(String(255))

    total_quantity: Mapped[int] = mapped_column(Integer)
    total_amount: Mapped[Numeric] = mapped_column(Numeric)
    total_orders: Mapped[int] = mapped_column(Integer)
    total_payments: Mapped[Numeric] = mapped_column(Numeric)
