from typing import List
from fastapi import APIRouter, Depends, UploadFile, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.background import BackgroundTasks
from fastapi.responses import FileResponse

from src.auth.manager import current_active_user
from src.database import get_async_session
from src.fault.dependencies import valid_image, valid_fault, valid_image_path
from src.fault.schemas import FaultRead
from src.fault.services import create_fault, get_faults, get_fault_with_full_link_image
from fastapi_cache.decorator import cache

fault_router = APIRouter(
    prefix="/fault",
    tags=['Fault']
)


@fault_router.get('/{fault_id}', response_model=FaultRead)
@cache(expire=60)
async def get_creator_fault_by_id(fault=Depends(valid_fault)):
    return fault


@fault_router.get('/{fault_id}/image/{image_id}')
async def get_image(
        image_path=Depends(valid_image_path)
):
    return FileResponse(path=image_path)


@fault_router.get('/', response_model=List[FaultRead])
async def get_creator_faults(
        request: Request,
        session: AsyncSession = Depends(get_async_session),
        user=Depends(current_active_user)
):
    faults = await get_faults(session, user.id)
    return [get_fault_with_full_link_image(fault, str(request.base_url)) for fault in faults]


@fault_router.post('/', response_model=FaultRead)
async def create_creator_fault(
        back_task: BackgroundTasks,
        request: Request,
        file: UploadFile = Depends(valid_image),
        description: str = Query(max_length=50),
        session: AsyncSession = Depends(get_async_session),
        user=Depends(current_active_user)
):
    fault = await create_fault(description, user, back_task, session, file)
    fault_pd = get_fault_with_full_link_image(fault, request)
    return fault_pd