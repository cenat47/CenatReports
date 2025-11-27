import asyncio
from src.tasks.celery_app import celery_app
from src.tasks.report import ReportService, get_db_np





@celery_app.task(name="make_report")
def make_report(task_id):
    asyncio.run(run_report(task_id))


async def run_report(task_id):
    async for db in get_db_np():
        service = ReportService(db=db)
        await service.make_report_h(task_id)
