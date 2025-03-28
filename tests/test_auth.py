import pytest
from httpx import AsyncClient
from app import schemas

@pytest.mark.asyncio
async def test_register_user(test_client):
    async with AsyncClient(app=test_client.app, base_url="http://test") as ac:
        response = await ac.post("/register", json={"email": "test@example.com", "password": "password123"})
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_login(test_client):
    async with AsyncClient(app=test_client.app, base_url="http://test") as ac:
        await ac.post("/register", json={"email": "test@example.com", "password": "password123"})
        response = await ac.post("/token", data={"username": "test@example.com", "password": "password123"})
    assert response.status_code == 200
    assert "access_token" in response.json()