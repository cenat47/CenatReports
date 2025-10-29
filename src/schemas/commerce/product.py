from pydantic import BaseModel, Field


class ProductAdd(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(ge=0)
    category_id: int
    supplier_id: int


class Product(ProductAdd):
    id: int
