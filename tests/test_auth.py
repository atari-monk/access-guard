import pytest
from httpx import AsyncClient
from app.main import app
from app.database import Base, engine

@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="module", autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.mark.anyio
async def test_full_flow():
    async with AsyncClient(app=app, base_url="http://test") as ac:

        r = await ac.post("/auth/register", json={"username": "alice", "password": "secret"})
        assert r.status_code == 200

        r = await ac.post("/auth/login", json={"username": "alice", "password": "secret"})
        assert r.status_code == 200
        token = r.json()["access_token"]
        assert token

        r = await ac.post("/permissions/create",
                          params={"resource": "door1", "action": "access", "role_name": "guard"})
        assert r.status_code == 200

        r = await ac.post("/roles/assign", json={"username": "alice", "role": "guard"})
        assert r.status_code == 200

        r = await ac.post("/permissions/check",
                          json={"username": "alice", "resource": "door1", "action": "access"})
        assert r.status_code == 200
        assert r.json()["allowed"] is True
