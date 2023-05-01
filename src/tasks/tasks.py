import asyncio

from celery import Celery
import smtplib
from email.message import EmailMessage
from src.database import async_session_maker
from src.fault.services import get_faults, get_fault_with_full_link_image
from src.config import EMAIL_FROM, EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD

celery_app = Celery('tasks', broker='redis://localhost')


def get_email_template_dashboard(email_to:str, faults):
    email = EmailMessage()
    email['Subject'] = "All faults"
    email['From'] = EMAIL_FROM
    email['To'] = email_to

    email.set_content(
        '<div>'
        'Hi, below are all your faults.'
        '<br>'
        '<br>'
        f'{faults}'
        '</div>',
        subtype='html'
    )
    return email


async def get_faults_report(user_id, base_url):
    async with async_session_maker() as session:
        faults_ = await get_faults(session, user_id)
    faults = [str(get_fault_with_full_link_image(fault, base_url).dict()) for fault in faults_]
    return " <br> ".join(faults)


@celery_app.task
def send_email_faults_report(email_to, user_id, base_url):
    email = get_email_template_dashboard(email_to, asyncio.run(get_faults_report(user_id, base_url)))
    with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as server:
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        server.send_message(email)