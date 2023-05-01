
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


async def create_fault(description, user, back_task, session, file):
    file_name = f'{uuid4()}.' + str(file.filename.split('.')[1])
    fault = Fault(description=description, creator_id=user.id, images=[Image(file_name=file_name)])
    back_task.add_task(write_image, os.path.join(BASE_DIR, 'media', str(user.id), file_name), file)
    session.add(fault)
    await session.commit()
    return fault


async def get_fault(fault_id, session):
    stmt = select(Fault).where(Fault.id == fault_id).options(selectinload(Fault.images))
    fault = await session.scalar(stmt)
    return fault


async def get_faults(session, user_id):
    stmt = select(Fault).where(Fault.creator_id == user_id).options(selectinload(Fault.images))
    faults = await session.execute(stmt)
    return faults.scalars().all()


async def get_image(image_id, session):
    image = await session.get(Image,image_id)
    return image


def get_fault_with_full_link_image(fault, base_url):
    fault_pd =FaultRead.from_orm(fault)
    for image in fault_pd.images:
        image.link = base_url + 'fault/' + str(fault_pd.id) + image.link
    return fault_pd