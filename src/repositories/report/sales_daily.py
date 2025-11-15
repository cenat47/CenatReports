from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from src.models.report.sales_daily import SalesDailyORM
from src.repositories.base import BaseRepository
from src.repositories.mapper.mappers import SalesDailyDataMapper


class SalesDailyRepository(BaseRepository):
    model = SalesDailyORM
    mapper = SalesDailyDataMapper

    async def get_sales_daily(self, date_from: date, date_to: date):
        query = (
            select(
                SalesDailyORM.date,
                SalesDailyORM.total_orders,
                SalesDailyORM.total_amount,
                SalesDailyORM.avg_check,
                SalesDailyORM.total_items,
                SalesDailyORM.total_payments,
            )
            .where(SalesDailyORM.date >= date_from)
            .where(SalesDailyORM.date <= date_to)
            .order_by(SalesDailyORM.date)
        )

        result = await self.session.execute(query)
        rows = result.all()

        return [self.mapper.map_to_domain_entity(row._mapping) for row in rows]
