from fastapi import APIRouter, Depends, Request

from src.project.dependencies import project_with_user_perm
from src.tasks.tasks import send_email_faults_report
from src.auth.manager import current_active_user


tasks_router = APIRouter(
    prefix="/report",
    tags=['Report']
)


@tasks_router.get('/')
async def get_faults_report(
        request: Request,
        user=Depends(current_active_user),
        project=Depends(project_with_user_perm)
):
    send_email_faults_report.delay(user.email, project.id, str(request.base_url))
    return {
        "status": 200,
        "data": "Report sent."
    }