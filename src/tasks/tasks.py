from src.utils.email_sender import send_verification_email
from src.tasks.celery_app import celery_app


@celery_app.task(name="send_verification_email")
def send_verification_email_task(to_email: str, code: str):
    send_verification_email(to_email, code)
