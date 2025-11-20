from datetime import date

from sqlalchemy import func, select
from src.schemas.report.sales_by_product_category_daily import (
    SalesByCategoryDaily,
    SalesByCategorySummary,
    SalesByProductDaily,
    SalesByProductSummary,
)
from src.models.report.sales_by_product_category_daily import (
    SalesByProductCategoryDailyORM,
)
from src.repositories.base import BaseRepository
from src.repositories.mapper.mappers import SalesByProductCategoryDailyDataMapper


from sqlalchemy import desc


class SalesByProductCategoryDailyRepository(BaseRepository):
    model = SalesByProductCategoryDailyORM
    mapper = SalesByProductCategoryDailyDataMapper

    async def get_sales_by_product_daily(
        self,
        date_from: date,
        date_to: date,
        product_id: int | None = None,
        product_name: str | None = None,
        top: int | None = None,
    ):
        query = (
            select(
                SalesByProductCategoryDailyORM.order_date,
                SalesByProductCategoryDailyORM.product_id,
                SalesByProductCategoryDailyORM.product_name,
                SalesByProductCategoryDailyORM.total_quantity,
                SalesByProductCategoryDailyORM.total_amount,
                SalesByProductCategoryDailyORM.total_orders,
                SalesByProductCategoryDailyORM.total_payments,
            )
            .where(SalesByProductCategoryDailyORM.order_date >= date_from)
            .where(SalesByProductCategoryDailyORM.order_date <= date_to)
        )

        if product_id is not None:
            query = query.where(SalesByProductCategoryDailyORM.product_id == product_id)

        if product_name:
            query = query.where(
                SalesByProductCategoryDailyORM.product_name.ilike(f"%{product_name}%")
            )

        query = query.order_by(
            SalesByProductCategoryDailyORM.order_date,
            SalesByProductCategoryDailyORM.product_name,
        )
        if top:
            query = query.limit(top)

        rows = (await self.session.execute(query)).all()
        return [SalesByProductDaily(**row._mapping) for row in rows]

    async def get_sales_by_product_summary(
        self,
        date_from: date,
        date_to: date,
        product_id: int | None = None,
        product_name: str | None = None,
        top: int | None = None,
    ):
        query = (
            select(
                SalesByProductCategoryDailyORM.product_id,
                SalesByProductCategoryDailyORM.product_name,
                func.sum(SalesByProductCategoryDailyORM.total_quantity).label(
                    "total_quantity"
                ),
                func.sum(SalesByProductCategoryDailyORM.total_amount).label(
                    "total_amount"
                ),
                func.sum(SalesByProductCategoryDailyORM.total_orders).label(
                    "total_orders"
                ),
                func.sum(SalesByProductCategoryDailyORM.total_payments).label(
                    "total_payments"
                ),
            )
            .where(SalesByProductCategoryDailyORM.order_date >= date_from)
            .where(SalesByProductCategoryDailyORM.order_date <= date_to)
            .group_by(
                SalesByProductCategoryDailyORM.product_id,
                SalesByProductCategoryDailyORM.product_name,
            )
        )

        if product_id:
            query = query.where(SalesByProductCategoryDailyORM.product_id == product_id)

        if product_name:
            query = query.where(
                SalesByProductCategoryDailyORM.product_name.ilike(f"%{product_name}%")
            )

        query = query.order_by(desc("total_amount"))

        if top:
            query = query.limit(top)

        rows = (await self.session.execute(query)).all()
        return [SalesByProductSummary(**row._mapping) for row in rows]

    async def get_sales_by_category_daily(
        self,
        date_from: date,
        date_to: date,
        category_id: int | None = None,
        category_name: str | None = None,
        top: int | None = None,
    ):
        query = (
            select(
                SalesByProductCategoryDailyORM.order_date,
                SalesByProductCategoryDailyORM.category_id,
                SalesByProductCategoryDailyORM.category_name,
                func.sum(SalesByProductCategoryDailyORM.total_quantity).label(
                    "total_quantity"
                ),
                func.sum(SalesByProductCategoryDailyORM.total_amount).label(
                    "total_amount"
                ),
                func.sum(SalesByProductCategoryDailyORM.total_orders).label(
                    "total_orders"
                ),
                func.sum(SalesByProductCategoryDailyORM.total_payments).label(
                    "total_payments"
                ),
            )
            .where(SalesByProductCategoryDailyORM.order_date >= date_from)
            .where(SalesByProductCategoryDailyORM.order_date <= date_to)
            .group_by(
                SalesByProductCategoryDailyORM.order_date,
                SalesByProductCategoryDailyORM.category_id,
                SalesByProductCategoryDailyORM.category_name,
            )
        )

        if category_id:
            query = query.where(
                SalesByProductCategoryDailyORM.category_id == category_id
            )

        if category_name:
            query = query.where(
                SalesByProductCategoryDailyORM.category_name.ilike(f"%{category_name}%")
            )

        query = query.order_by(
            SalesByProductCategoryDailyORM.order_date,
            SalesByProductCategoryDailyORM.category_name,
        )
        if top:
            query = query.limit(top)

        rows = (await self.session.execute(query)).all()
        return [SalesByCategoryDaily(**row._mapping) for row in rows]

    async def get_sales_by_category_summary(
        self,
        date_from: date,
        date_to: date,
        category_id: int | None = None,
        category_name: str | None = None,
        top: int | None = None,
    ):
        query = (
            select(
                SalesByProductCategoryDailyORM.category_id,
                SalesByProductCategoryDailyORM.category_name,
                func.sum(SalesByProductCategoryDailyORM.total_quantity).label(
                    "total_quantity"
                ),
                func.sum(SalesByProductCategoryDailyORM.total_amount).label(
                    "total_amount"
                ),
                func.sum(SalesByProductCategoryDailyORM.total_orders).label(
                    "total_orders"
                ),
                func.sum(SalesByProductCategoryDailyORM.total_payments).label(
                    "total_payments"
                ),
            )
            .where(SalesByProductCategoryDailyORM.order_date >= date_from)
            .where(SalesByProductCategoryDailyORM.order_date <= date_to)
            .group_by(
                SalesByProductCategoryDailyORM.category_id,
                SalesByProductCategoryDailyORM.category_name,
            )
        )

        if category_id:
            query = query.where(
                SalesByProductCategoryDailyORM.category_id == category_id
            )

        if category_name:
            query = query.where(
                SalesByProductCategoryDailyORM.category_name.ilike(f"%{category_name}%")
            )

        query = query.order_by(desc("total_amount"))

        if top:
            query = query.limit(top)

        rows = (await self.session.execute(query)).all()
        return [SalesByCategorySummary(**row._mapping) for row in rows]
