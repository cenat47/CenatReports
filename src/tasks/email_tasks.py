from src.tasks.celery_app import celery_app
from src.utils.email_sender import send_report_ready_email, send_verification_email


@celery_app.task(name="send_verification_email")
def send_verification_email_task(to_email: str, code: str):
    send_verification_email(to_email, code)



@celery_app.task(name="send_report_ready_email")
def send_report_ready_email_task(to_email: str, report_name: str, report_link: str):
    send_report_ready_email(to_email, report_name, report_link)
