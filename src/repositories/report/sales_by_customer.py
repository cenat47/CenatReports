from datetime import date
from sqlalchemy import select, func, desc

from src.models.report.sales_by_customer import SalesByCustomerDailyORM
from src.repositories.base import BaseRepository
from src.schemas.report.sales_by_customer import (
    SalesByCustomerDaily,
    SalesByCustomerSummary,
)


class SalesByCustomerRepository(BaseRepository):
    model = SalesByCustomerDailyORM

    async def get_sales_by_customer_daily(
        self,
        date_from: date,
        date_to: date,
        customer_id: int | None = None,
        customer_name: str | None = None,
        top: int | None = None,
    ):
        query = (
            select(
                SalesByCustomerDailyORM.order_date,
                SalesByCustomerDailyORM.customer_id,
                SalesByCustomerDailyORM.customer_name,
                SalesByCustomerDailyORM.customer_email,
                SalesByCustomerDailyORM.total_quantity,
                SalesByCustomerDailyORM.total_amount,
                SalesByCustomerDailyORM.total_orders,
                SalesByCustomerDailyORM.total_payments,
            )
            .where(SalesByCustomerDailyORM.order_date >= date_from)
            .where(SalesByCustomerDailyORM.order_date <= date_to)
        )

        if customer_id is not None:
            query = query.where(SalesByCustomerDailyORM.customer_id == customer_id)

        if customer_name:
            query = query.where(
                SalesByCustomerDailyORM.customer_name.ilike(f"%{customer_name}%")
            )

        query = query.order_by(
            SalesByCustomerDailyORM.order_date,
            SalesByCustomerDailyORM.customer_name,
        )
        if top:
            query = query.limit(top)
        rows = (await self.session.execute(query)).all()
        return [SalesByCustomerDaily(**row._mapping) for row in rows]

    async def get_sales_by_customer_summary(
        self,
        date_from: date,
        date_to: date,
        customer_id: int | None = None,
        customer_name: str | None = None,
        top: int | None = None,
    ):
        query = (
            select(
                SalesByCustomerDailyORM.customer_id,
                SalesByCustomerDailyORM.customer_name,
                SalesByCustomerDailyORM.customer_email,
                func.sum(SalesByCustomerDailyORM.total_quantity).label(
                    "total_quantity"
                ),
                func.sum(SalesByCustomerDailyORM.total_amount).label("total_amount"),
                func.sum(SalesByCustomerDailyORM.total_orders).label("total_orders"),
                func.sum(SalesByCustomerDailyORM.total_payments).label(
                    "total_payments"
                ),
            )
            .where(SalesByCustomerDailyORM.order_date >= date_from)
            .where(SalesByCustomerDailyORM.order_date <= date_to)
            .group_by(
                SalesByCustomerDailyORM.customer_id,
                SalesByCustomerDailyORM.customer_name,
                SalesByCustomerDailyORM.customer_email,
            )
        )

        if customer_id is not None:
            query = query.where(SalesByCustomerDailyORM.customer_id == customer_id)

        if customer_name:
            query = query.where(
                SalesByCustomerDailyORM.customer_name.ilike(f"%{customer_name}%")
            )

        query = query.order_by(desc("total_amount"))

        if top:
            query = query.limit(top)

        rows = (await self.session.execute(query)).all()
        return [SalesByCustomerSummary(**row._mapping) for row in rows]
