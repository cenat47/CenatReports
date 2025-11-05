from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader, select_autoescape
from aiosmtplib import send
from config import settings
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "email"

env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR), autoescape=select_autoescape(["html"])
)


async def send_verification_email(to_email: str, code: str):
    template = env.get_template("verification.html")
    html_content = template.render(code=code)

    message = EmailMessage()
    message["From"] = settings.SMTP_USER
    message["To"] = to_email
    message["Subject"] = "Подтверждение регистрации"
    message.set_content(html_content, subtype="html")

    await send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASS,
        start_tls=True,
    )
