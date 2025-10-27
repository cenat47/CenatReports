from sqlalchemy import String
from sqlalchemy.orm import (Mapped, declarative_base, mapped_column,
                            relationship)

from src.database import Base


class SupplierOrm(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    contact_info: Mapped[str] = mapped_column(String(200), nullable=True, index=True)

    products: Mapped[list["ProductOrm"]] = relationship(back_populates="supplier")
