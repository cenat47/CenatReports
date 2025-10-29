from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class CustomerORM(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    email: Mapped[str] = mapped_column(String(100), index=True)
    phone: Mapped[str] = mapped_column(String(20), index=True)
    address: Mapped[str] = mapped_column(String(200))

    orders: Mapped[list["OrderORM"]] = relationship(back_populates="customer")
