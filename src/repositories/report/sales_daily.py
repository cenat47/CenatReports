from datetime import date

from sqlalchemy import func, select
from src.schemas.report.sales_daily import SalesSummary
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

    async def get_sales_summary(self, date_from: date, date_to: date):
        query = (
            select(
                func.sum(SalesDailyORM.total_orders).label("total_orders"),
                func.sum(SalesDailyORM.total_amount).label("total_amount"),
                func.avg(SalesDailyORM.avg_check).label("avg_check"),
                func.sum(SalesDailyORM.total_items).label("total_items"),
                func.sum(SalesDailyORM.total_payments).label("total_payments"),
            )
            .where(SalesDailyORM.date >= date_from)
            .where(SalesDailyORM.date <= date_to)
        )

        result = await self.session.execute(query)
        row = result.one()
        data = dict(row._mapping)
        return SalesSummary(**data)
