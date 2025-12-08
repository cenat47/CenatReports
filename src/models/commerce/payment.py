from datetime import datetime

from sqlalchemy import DECIMAL, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class PaymentORM(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    payment_date: Mapped[datetime] = mapped_column(index=True)
    amount: Mapped[float] = mapped_column(DECIMAL(10, 2))
    method: Mapped[str] = mapped_column(String(50), index=True)

    order: Mapped["OrderORM"] = relationship(back_populates="payments")  # noqa F821
