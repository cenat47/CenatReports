from sqlalchemy import Integer, ForeignKey, DECIMAL, Computed
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base
from src.database import Base


class OrderItemOrm(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(DECIMAL(10, 2))
    total_cost: Mapped[float] = mapped_column(
        DECIMAL(10, 2), Computed("quantity * price")
    )

    order: Mapped["OrderOrm"] = relationship(back_populates="order_items")
    product: Mapped["ProductOrm"] = relationship(back_populates="order_items")
