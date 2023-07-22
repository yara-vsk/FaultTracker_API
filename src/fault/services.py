
import os
from uuid import uuid4
import aiofiles as aiofiles
from sqlalchemy import select, func, literal, String
from sqlalchemy.orm import selectinload, with_expression, contains_eager, joinedload, aliased

from src.config import BASE_DIR
from src.fault.models import Fault, Image
from src.fault.schemas import FaultRead

DEFAULT_CHUNK_SIZE = 1024 * 1024 * 1  # 1 megabyte


async def write_image(file_name, file):
    async with aiofiles.open(file_name,'wb') as buffer:
        while chunk := await file.read(DEFAULT_CHUNK_SIZE):
            await buffer.write(chunk)


def delete_image(file_path):
    os.remove(file_path)


async def create_fault_srv(description, project_id, user, back_task, session, file):
    file_name = f'{uuid4()}.' + str(file.filename.split('.')[1])
    fault = Fault(description=description, creator_id=user.id, project_id=project_id, images=[Image(file_name=file_name)])
    back_task.add_task(write_image, os.path.join(BASE_DIR, 'media', str(user.id), file_name), file)
    session.add(fault)
    await session.commit()
    return fault


async def update_fault(fault, description, back_task, session, file):
    if description:
        fault.description = description
    if file:
        for image in fault.images:
            back_task.add_task(delete_image, os.path.join(BASE_DIR, 'media', str(fault.creator_id), image.file_name))
            await session.delete(image)
        file_name = f'{uuid4()}.' + str(file.filename.split('.')[1])
        fault.images=[Image(file_name=file_name)]
        back_task.add_task(write_image, os.path.join(BASE_DIR, 'media', str(fault.creator_id), file_name), file)
    await session.commit()
    return fault


async def get_fault(fault_id, session):
    stmt = select(Fault).where(Fault.id == fault_id).options(selectinload(Fault.images))
    fault = await session.scalar(stmt)
    return fault


async def delete_fault(fault, session, back_task):
    images = fault.images
    for image in images:
        back_task.add_task(delete_image, os.path.join(BASE_DIR, 'media', str(fault.creator_id), image.file_name))
    await session.delete(fault)
    await session.commit()
    return


async def get_faults_srv(session, project_id):
    stmt = select(Fault).where(Fault.project_id == project_id).options(selectinload(Fault.images))
    faults = await session.execute(stmt)
    return faults.scalars().all()


async def get_image(image_id, session):
    image = await session.get(Image,image_id)
    return image


def get_fault_with_full_link_image(fault, base_url):
    fault_pd =FaultRead.from_orm(fault)
    for image in fault_pd.images:
        image.link = str(base_url) + 'project/' + str(fault_pd.project_id) + '/' + 'fault/' + str(fault_pd.id) + image.link
    return fault_pd