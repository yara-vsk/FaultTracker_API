from typing import List, Annotated, Union
from fastapi import APIRouter, Depends, UploadFile, Query, Request, Body
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.background import BackgroundTasks
from fastapi.responses import FileResponse

from src.auth.manager import current_active_user
from src.database import get_async_session
from src.fault.dependencies import valid_image, valid_fault, valid_image_path
from src.fault.schemas import FaultRead
from src.fault.services import create_fault_srv, get_faults_srv, get_fault_with_full_link_image, delete_fault, update_fault
from fastapi_cache.decorator import cache

from src.project.dependencies import valid_project, project_with_user_perm
from src.project.models import Project

fault_router = APIRouter(
    prefix="/project/{project_id}/fault",
    tags=['Fault'],
    dependencies=[Depends(project_with_user_perm),]
)


@fault_router.get('/{fault_id}', response_model=FaultRead)
@cache(expire=60)
async def get_fault_by_id(
        request: Request,
        fault=Depends(valid_fault)
):
    fault_pd = get_fault_with_full_link_image(fault, request.base_url)
    return fault_pd


@fault_router.delete('/{fault_id}', response_model=FaultRead)
async def delete_fault_by_id(
        request: Request,
        back_task: BackgroundTasks,
        fault=Depends(valid_fault),
        session: AsyncSession = Depends(get_async_session),
):
    await delete_fault(fault, session, back_task)
    fault_pd = get_fault_with_full_link_image(fault, request.base_url)
    return fault_pd


@fault_router.put('/{fault_id}', response_model=FaultRead)
async def update_fault_by_id(
        back_task: BackgroundTasks,
        request: Request,
        description: str | None = Body(max_length=50),
        file: Union[UploadFile, None] = None,
        fault=Depends(valid_fault),
        session: AsyncSession = Depends(get_async_session),
):
    if file:
        valid_image(file)
    fault_update = await update_fault(fault, description, back_task, session, file)
    fault_pd = get_fault_with_full_link_image(fault_update, request.base_url)
    return fault_pd


@fault_router.get('/{fault_id}/image/{image_id}')
async def get_image(
        image_path=Depends(valid_image_path)
):
    return FileResponse(path=image_path)


@fault_router.get('/', response_model=List[FaultRead])
async def get_faults(
        request: Request,
        project: Project = Depends(project_with_user_perm),
        session: AsyncSession = Depends(get_async_session)
):
    faults = await get_faults_srv(session, project.id)
    return [get_fault_with_full_link_image(fault, request.base_url) for fault in faults]


@fault_router.post('/', response_model=FaultRead)
async def create_fault(
        back_task: BackgroundTasks,
        request: Request,
        project: Project = Depends(project_with_user_perm),
        file: UploadFile = Depends(valid_image),
        description: str = Body(max_length=50),
        session: AsyncSession = Depends(get_async_session),
        user=Depends(current_active_user)
):
    fault = await create_fault_srv(description, project.id, user, back_task, session, file)
    fault_pd = get_fault_with_full_link_image(fault, request.base_url)
    return fault_pd