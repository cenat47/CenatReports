import asyncio
from src.tasks.celery_app import celery_app
from src.tasks.report import ReportService, get_db_np
from sqlalchemy import text


@celery_app.task(name="make_report")
def make_report(task_id):
    asyncio.run(run_report(task_id))


@celery_app.task(name="refresh_materialized_views")
def refresh_materialized_views():
    asyncio.run(_refresh_materialized_views())


async def _refresh_materialized_views():
    views = [
        "mv_sales_daily",
        "mv_sales_by_product_category_daily",
        "mv_sales_by_customer_daily",
        "mv_payments_by_method_daily",
    ]

    async for db in get_db_np():
        async with db.session.begin():
            for view in views:
                await db.session.execute(text(f"REFRESH MATERIALIZED VIEW {view};"))


async def run_report(task_id):
    async for db in get_db_np():
        service = ReportService(db=db)
        await service.make_report_h(task_id)
