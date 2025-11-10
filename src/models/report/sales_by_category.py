from sqlalchemy import String, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base


class SalesByCategoryORM(Base):
    __tablename__ = "mv_sales_by_category"

    category_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category_name: Mapped[str] = mapped_column(String(100))
    total_quantity: Mapped[int] = mapped_column(Integer)
    total_amount: Mapped[Numeric] = mapped_column(Numeric)
    total_orders: Mapped[int] = mapped_column(Integer)
    total_payments: Mapped[Numeric] = mapped_column(Numeric)
