from pydantic import BaseModel
from datetime import date
from decimal import Decimal


class SalesDailyParams(BaseModel):
    date_from: date
    date_to: date


class SalesDaily(BaseModel):
    date: date
    total_orders: int
    total_amount: Decimal
    avg_check: Decimal
    total_items: int
    total_payments: Decimal


class SalesSummary(BaseModel):
    total_orders: int
    total_amount: Decimal
    avg_check: Decimal
    total_items: int
    total_payments: Decimal
