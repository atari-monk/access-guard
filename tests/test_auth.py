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

        # 1️⃣ Rejestracja użytkownika
        r = await ac.post("/auth/register", json={"username": "alice", "password": "secret"})
        assert r.status_code == 200

        # 2️⃣ Logowanie -> pobranie JWT
        r = await ac.post("/auth/login", json={"username": "alice", "password": "secret"})
        assert r.status_code == 200
        token = r.json()["access_token"]
        assert token

        # Nagłówek Authorization
        headers = {"Authorization": f"Bearer {token}"}

        # 3️⃣ Tworzenie uprawnienia dla roli
        r = await ac.post(
            "/permissions/create",
            json={"resource": "door1", "action": "access", "role_name": "guard"},
            headers=headers
        )
        assert r.status_code == 200

        # 4️⃣ Przypisanie roli użytkownikowi
        r = await ac.post(
            "/roles/assign",
            json={"username": "alice", "role": "guard"},
            headers=headers
        )
        assert r.status_code == 200
        data = r.json()
        assert data["username"] == "alice"
        assert "guard" in data["roles"]

        # 5️⃣ Sprawdzenie uprawnienia użytkownika (bez username w payload)
        r = await ac.post(
            "/permissions/check",
            json={"resource": "door1", "action": "access"},
            headers=headers
        )
        assert r.status_code == 200
        assert r.json()["allowed"] is True
