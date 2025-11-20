from pydantic import BaseModel
from datetime import date
from decimal import Decimal


class SalesByProductDailyParams(BaseModel):
    date_from: date
    date_to: date
    product_id: int | None = None
    product_name: str | None = None
    top: int | None = None  # топ товаров по total_amount


class SalesByCategoryDailyParams(BaseModel):
    date_from: date
    date_to: date
    category_id: int | None = None
    category_name: str | None = None
    top: int | None = None  # топ категорий по total_amount


class SalesByProductDaily(BaseModel):
    order_date: date
    product_id: int
    product_name: str
    total_quantity: int
    total_amount: Decimal
    total_orders: int
    total_payments: Decimal


class SalesByCategoryDaily(BaseModel):
    order_date: date
    category_id: int
    category_name: str
    total_quantity: int
    total_amount: Decimal
    total_orders: int
    total_payments: Decimal


class SalesByProductSummary(BaseModel):
    product_id: int | None = None
    product_name: str | None = None
    total_quantity: int = 0
    total_amount: Decimal = Decimal("0")
    total_orders: int = 0
    total_payments: Decimal = Decimal("0")


class SalesByCategorySummary(BaseModel):
    category_id: int | None = None
    category_name: str | None = None
    total_quantity: int = 0
    total_amount: Decimal = Decimal("0")
    total_orders: int = 0
    total_payments: Decimal = Decimal("0")
