import asyncio
from src.tasks.celery_app import celery_app
from src.tasks.report import ReportService, get_db_np
from sqlalchemy import text
from src.siem import log_event, set_correlation_id


@celery_app.task(name="make_report")
def make_report(task_id):
    asyncio.run(run_report(task_id))


@celery_app.task(name="refresh_materialized_views")
def refresh_materialized_views():
    asyncio.run(_refresh_materialized_views())


async def _refresh_materialized_views():
    set_correlation_id()

    await log_event("materialized_views_refresh_started")

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

    await log_event("materialized_views_refresh_finished")


async def run_report(task_id):
    set_correlation_id()

    await log_event(
        "celery_report_started",
        details={
            "report.task_id": task_id,
        },
    )

    async for db in get_db_np():
        service = ReportService(db=db)
        await service.make_report_h(task_id)

    await log_event(
        "celery_report_finished",
        details={
            "report.task_id": task_id,
        },
    )