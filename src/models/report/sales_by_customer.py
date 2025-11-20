from sqlalchemy import String, Numeric, Integer, Date
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base


class SalesByCustomerDailyORM(Base):
    __tablename__ = "mv_sales_by_customer_daily"

    # PK: комбинация дня и клиента
    order_date: Mapped[Date] = mapped_column(Date, primary_key=True)
    customer_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    customer_name: Mapped[str] = mapped_column(String(100))
    customer_email: Mapped[str] = mapped_column(String(100))

    total_quantity: Mapped[int] = mapped_column(Integer)
    total_amount: Mapped[Numeric] = mapped_column(Numeric)
    total_orders: Mapped[int] = mapped_column(Integer)
    total_payments: Mapped[Numeric] = mapped_column(Numeric)
