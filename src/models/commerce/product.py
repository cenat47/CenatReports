from sqlalchemy import String, ForeignKey, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship


from src.database import Base


class ProductOrm(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    price: Mapped[float] = mapped_column(DECIMAL(10, 2))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"))

    category: Mapped["CategoryOrm"] = relationship(back_populates="products")
    supplier: Mapped["SupplierOrm"] = relationship(back_populates="products")
    order_items: Mapped[list["OrderItemOrm"]] = relationship(back_populates="product")
