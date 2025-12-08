from sqlalchemy import DECIMAL, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class ProductORM(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    price: Mapped[float] = mapped_column(DECIMAL(10, 2))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"))

    category: Mapped["CategoryORM"] = relationship(back_populates="products")  # noqa F821
    supplier: Mapped["SupplierORM"] = relationship(back_populates="products")  # noqa F821
    order_items: Mapped[list["OrderItemOrm"]] = relationship(back_populates="product")  # noqa F821
