import pytest
from httpx import AsyncClient
from app import models

@pytest.mark.asyncio
async def test_create_short_link(test_client, mock_redis):
    async with AsyncClient(app=test_client.app, base_url="http://test") as ac:
        await ac.post("/register", json={"email": "user@example.com", "password": "pass123"})
        token_response = await ac.post("/token", data={"username": "user@example.com", "password": "pass123"})
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.post(
            "/links/shorten",
            json={"original_url": "https://example.com"},
            headers=headers
        )
    assert response.status_code == 200
    assert "short_code" in response.json()

@pytest.mark.asyncio
async def test_redirect(test_client, mock_redis):
    async with AsyncClient(app=test_client.app, base_url="http://test") as ac:
        await ac.post("/register", json={"email": "user@example.com", "password": "pass123"})
        token_response = await ac.post("/token", data={"username": "user@example.com", "password": "pass123"})
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        link_response = await ac.post(
            "/links/shorten",
            json={"original_url": "https://example.com"},
            headers=headers
        )
        short_code = link_response.json()["short_code"]
        response = await ac.get(f"/{short_code}", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com"

@pytest.mark.asyncio
async def test_invalid_data(test_client, mock_redis):
    async with AsyncClient(app=test_client.app, base_url="http://test") as ac:
        await ac.post("/register", json={"email": "user@example.com", "password": "pass123"})
        token_response = await ac.post("/token", data={"username": "user@example.com", "password": "pass123"})
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.post(
            "/links/shorten",
            json={"original_url": "not-a-url"},
            headers=headers
        )
    assert response.status_code == 422