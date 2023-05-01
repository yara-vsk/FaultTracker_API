import os
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.fault.models import Fault
from tests.conftest import async_session_maker

file_path = os.path.join(os.path.dirname(__file__), 'media_for_tests', 'image_test.jpg')


async def test_create_creator_fault(ac: AsyncClient):
    response = await ac.post('auth/jwt/login', data={
        "username": "user@example.com",
        "password": "string",
    })
    access_token = "Bearer " + str(response.json()['access_token'])
    with open(file_path, 'rb') as file:
        response2 = await ac.post('fault/',
                                  headers={
                                      "Authorization": access_token},
                                  params={
                                      "description": "Test description.",
                                  },
                                  files={'file': file}
                                  )
    async with async_session_maker() as session:
        stmt = select(Fault).where(Fault.id == 1).options(selectinload(Fault.images))
        fault = await session.scalar(stmt)
    assert response.status_code == 200
    assert response2.status_code == 200
    assert response2.json()['description'] == "Test description."
    assert response2.json()['id'] == 1
    assert os.path.isfile(os.path.join(os.path.dirname(os.path.dirname(__file__)),'media', str(fault.images[0].file_name))) == True
