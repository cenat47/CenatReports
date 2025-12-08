from datetime import date

from sqlalchemy import DECIMAL, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class OrderORM(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    order_date: Mapped[date] = mapped_column(index=True)
    status: Mapped[str] = mapped_column(String(50), index=True)
    total_amount: Mapped[float] = mapped_column(DECIMAL(10, 2))

    customer: Mapped["CustomerORM"] = relationship(back_populates="orders")  # noqa F821
    order_items: Mapped[list["OrderItemOrm"]] = relationship(back_populates="order")  # noqa F821
    payments: Mapped[list["PaymentORM"]] = relationship(back_populates="order")  # noqa F821
