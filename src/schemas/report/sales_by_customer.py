from pydantic import BaseModel
from datetime import date
from decimal import Decimal


class SalesByCustomerParams(BaseModel):
    date_from: date
    date_to: date

    customer_id: int | None = None
    customer_name: str | None = None

    # summary-only option
    top: int | None = None


class SalesByCustomerDaily(BaseModel):
    order_date: date

    customer_id: int
    customer_name: str
    customer_email: str

    total_quantity: int
    total_amount: Decimal
    total_orders: int
    total_payments: Decimal


class SalesByCustomerSummary(BaseModel):
    customer_id: int
    customer_name: str
    customer_email: str

    total_quantity: int
    total_amount: Decimal
    total_orders: int
    total_payments: Decimal
