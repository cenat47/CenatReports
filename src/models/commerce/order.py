from datetime import date

from sqlalchemy import DECIMAL, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class OrderOrm(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    order_date: Mapped[date] = mapped_column(index=True)
    status: Mapped[str] = mapped_column(String(50), index=True)
    total_amount: Mapped[float] = mapped_column(DECIMAL(10, 2))

    customer: Mapped["CustomerOrm"] = relationship(back_populates="orders")
    order_items: Mapped[list["OrderItemOrm"]] = relationship(back_populates="order")
    payments: Mapped[list["PaymentOrm"]] = relationship(back_populates="order")
