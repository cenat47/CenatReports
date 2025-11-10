from sqlalchemy import String, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base


class PaymentsByMethodORM(Base):
    __tablename__ = "mv_payments_by_method"

    payment_method: Mapped[str] = mapped_column(String(50), primary_key=True)
    total_orders: Mapped[int] = mapped_column(Integer)
    total_quantity: Mapped[int] = mapped_column(Integer)
    total_amount: Mapped[Numeric] = mapped_column(Numeric)
    total_payments: Mapped[Numeric] = mapped_column(Numeric)
