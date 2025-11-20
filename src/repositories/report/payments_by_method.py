from pendulum import date
from sqlalchemy import select, func, desc

from src.models.report.payments_by_method import PaymentsByMethodDailyORM
from src.repositories.base import BaseRepository
from src.schemas.report.payments_by_method import (
    PaymentsByMethodDaily,
    PaymentsByMethodSummary,
)


class PaymentsRepository(BaseRepository):
    model = PaymentsByMethodDailyORM

    async def get_payments_daily(
        self,
        date_from: date,
        date_to: date,
        payment_method: str | None = None,
        top: int | None = None,
    ):
        query = (
            select(
                self.model.payment_date,
                self.model.payment_method,
                self.model.total_orders,
                self.model.total_quantity,
                self.model.total_amount,
                self.model.total_payments,
            )
            .where(self.model.payment_date >= date_from)
            .where(self.model.payment_date <= date_to)
        )

        if payment_method:
            query = query.where(self.model.payment_method == payment_method)

        query = query.order_by(self.model.payment_date, self.model.payment_method)
        if top:
            query = query.limit(top)
        rows = (await self.session.execute(query)).all()
        return [PaymentsByMethodDaily(**row._mapping) for row in rows]

    async def get_payments_summary(
        self,
        date_from: date,
        date_to: date,
        payment_method: str | None = None,
        top: int | None = None,
    ):
        query = (
            select(
                self.model.payment_method,
                func.sum(self.model.total_orders).label("total_orders"),
                func.sum(self.model.total_quantity).label("total_quantity"),
                func.sum(self.model.total_amount).label("total_amount"),
                func.sum(self.model.total_payments).label("total_payments"),
            )
            .where(self.model.payment_date >= date_from)
            .where(self.model.payment_date <= date_to)
            .group_by(self.model.payment_method)
        )

        if payment_method:
            query = query.where(self.model.payment_method == payment_method)

        query = query.order_by(desc("total_payments"))

        if top:
            query = query.limit(top)

        rows = (await self.session.execute(query)).all()
        return [PaymentsByMethodSummary(**row._mapping) for row in rows]
