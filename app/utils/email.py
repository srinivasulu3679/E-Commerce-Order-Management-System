import logging
import smtplib
from email.message import EmailMessage

from app.database import settings


logger = logging.getLogger(__name__)


def send_email(
    to_email: str,
    subject: str,
    body: str,
) -> None:
    """
    Send an email using SMTP.

    Email errors are logged and do not break the API request.
    """

    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.warning(
            "SMTP is not configured. Email was not sent to %s.",
            to_email,
        )
        return

    try:
        message = EmailMessage()
        message["From"] = settings.SMTP_USER
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)

        with smtplib.SMTP(
            settings.SMTP_HOST,
            settings.SMTP_PORT,
            timeout=10,
        ) as server:
            server.starttls()

            if settings.SMTP_PASSWORD:
                server.login(
                    settings.SMTP_USER,
                    settings.SMTP_PASSWORD,
                )

            server.send_message(message)

    except Exception:
        logger.exception(
            "Failed to send email to %s",
            to_email,
        )