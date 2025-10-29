from pydantic import BaseModel, Field


class SupplierAdd(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    contact_info: str | None = Field(default=None, max_length=200)


class Supplier(SupplierAdd):
    id: int
