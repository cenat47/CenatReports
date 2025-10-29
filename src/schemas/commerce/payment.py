from datetime import datetime
from pydantic import BaseModel, Field


class PaymentAdd(BaseModel):
    order_id: int
    payment_date: datetime
    amount: float = Field(ge=0)
    method: str = Field(min_length=1, max_length=50)


class Payment(PaymentAdd):
    id: int
