import asyncio
from src.utils.email_sender import send_verification_email
from src.tasks.celery_app import celery_app
from src.tasks.report import ReportService, get_db_np


@celery_app.task(name="send_verification_email")
def send_verification_email_task(to_email: str, code: str):
    send_verification_email(to_email, code)


@celery_app.task(name="make_report")
def make_report(task_id):
    asyncio.run(run_report(task_id))


async def run_report(task_id):
    async for db in get_db_np():
        service = ReportService(db=db)
        await service.make_report_h(task_id)
