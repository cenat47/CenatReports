from src.tasks.celery_app import celery_app
from src.utils.email_sender import (
    send_report_ready_email,
    send_role_change_email,
    send_verification_email,
)
from src.siem import log_event, set_correlation_id
import asyncio


@celery_app.task(name="send_verification_email")
def send_verification_email_task(to_email: str, code: str):
    set_correlation_id()
    asyncio.run(
        log_event(
            "email_verification_sent",
            details={
                "email.to": to_email,
                "email.type": "verification",
            },
        )
    )
    send_verification_email(to_email, code)


@celery_app.task(name="send_role_change_email_task")
def send_role_change_email_task(
    admin_email: str, target_email: str, new_role: str, code: str
):
    set_correlation_id()
    asyncio.run(
        log_event(
            "email_role_change_sent",
            details={
                "email.admin": admin_email,
                "email.target": target_email,
                "target.role": new_role,
                "email.type": "role_change",
            },
            severity="warning",
        )
    )
    send_role_change_email(admin_email, target_email, new_role, code)


@celery_app.task(name="send_report_ready_email")
def send_report_ready_email_task(to_email: str, report_name: str, report_link: str):
    set_correlation_id()
    asyncio.run(
        log_event(
            "email_report_ready_sent",
            details={
                "email.to": to_email,
                "report.name": report_name,
                "email.type": "report_ready",
            },
        )
    )
    send_report_ready_email(to_email, report_name, report_link)