from pydantic import BaseModel
from datetime import date
from decimal import Decimal


class PaymentsByMethodDaily(BaseModel):
    payment_date: date
    payment_method: str
    total_orders: int
    total_quantity: int
    total_amount: Decimal
    total_payments: Decimal


class PaymentsByMethodSummary(BaseModel):
    payment_method: str
    total_orders: int
    total_quantity: int
    total_amount: Decimal
    total_payments: Decimal


class PaymentsReportParams(BaseModel):
    date_from: date
    date_to: date
    payment_method: str | None = None
    top: int | None = None
