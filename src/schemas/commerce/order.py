from datetime import date

from pydantic import BaseModel, Field


class OrderAdd(BaseModel):
    customer_id: int
    order_date: date
    status: str = Field(min_length=1, max_length=50)
    total_amount: float = Field(ge=0)


class Order(OrderAdd):
    id: int
