from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader, select_autoescape
import smtplib
from src.config import settings
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "email"

env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR), autoescape=select_autoescape(["html"])
)


def send_verification_email(to_email: str, code: str):
    template = env.get_template("verification.html")
    html_content = template.render(code=code)

    message = EmailMessage()
    message["From"] = settings.SMTP_USER
    message["To"] = to_email
    message["Subject"] = "Подтверждение регистрации"
    message.set_content(html_content, subtype="html")

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
        smtp.login(settings.SMTP_USER, settings.SMTP_PASS)
        smtp.send_message(message)


def send_role_change_email(
    admin_email: str, target_email: str, new_role: str, code: str
):
    template = env.get_template("role_change_verification.html")
    html_content = template.render(
        code=code, new_role=new_role, admin_email=admin_email, target_email=target_email
    )

    message = EmailMessage()
    message["From"] = settings.SMTP_USER
    message["To"] = admin_email  # ← Письмо отправляем админу
    message["Subject"] = "Подтверждение изменения роли пользователя"
    message.set_content(html_content, subtype="html")

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
        smtp.login(settings.SMTP_USER, settings.SMTP_PASS)
        smtp.send_message(message)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
        smtp.login(settings.SMTP_USER, settings.SMTP_PASS)
        smtp.send_message(message)


def send_report_ready_email(to_email: str, report_name: str, report_link: str):
    template = env.get_template("report_ready.html")
    html_content = template.render(report_name=report_name, report_link=report_link)

    message = EmailMessage()
    message["From"] = settings.SMTP_USER
    message["To"] = to_email
    message["Subject"] = f"Отчет '{report_name}' готов"
    message.set_content(html_content, subtype="html")

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
        smtp.login(settings.SMTP_USER, settings.SMTP_PASS)
        smtp.send_message(message)
