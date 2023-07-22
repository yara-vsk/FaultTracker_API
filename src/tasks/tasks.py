import asyncio

from celery import Celery
import smtplib
from email.message import EmailMessage
from src.database import async_session_maker
from src.fault.services import get_faults_srv, get_fault_with_full_link_image
from src.config import EMAIL_FROM, EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, REDIS_HOST, REDIS_PORT

celery_app = Celery('tasks', broker=f'redis://{REDIS_HOST}:{REDIS_PORT}')


def get_email_template_dashboard(email_to:str, faults,project_id):
    email = EmailMessage()
    email['Subject'] = "All faults"
    email['From'] = EMAIL_FROM
    email['To'] = email_to

    email.set_content(
        '<div>'
        f'Hi, below are all project id {project_id} faults.'
        '<br>'
        '<br>'
        f'{faults}'
        '</div>',
        subtype='html'
    )
    return email


async def get_faults_report(project_id, base_url):
    async with async_session_maker() as session:
        faults_ = await get_faults_srv(session, project_id)
    faults = [str(get_fault_with_full_link_image(fault, base_url).dict()) for fault in faults_]
    return " <br> ".join(faults)


@celery_app.task
def send_email_faults_report(email_to, project_id, base_url):
    email = get_email_template_dashboard(email_to, asyncio.run(get_faults_report(project_id, base_url)),project_id)
    with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as server:
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        server.send_message(email)