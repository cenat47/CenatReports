from pydantic import BaseModel, Field


class OrderItemAdd(BaseModel):
    order_id: int
    product_id: int
    quantity: int = Field(ge=1)
    price: float = Field(ge=0)
    total_cost: float | None = None  # вычисляется как quantity * price


class OrderItem(OrderItemAdd):
    id: int
