from sqlalchemy.orm import Session
from app import crud, auth, models

class AuthService:
    @staticmethod
    def register_user(db: Session, username: str, password: str) -> models.User:
        existing = crud.get_user_by_username(db, username)
        if existing:
            raise ValueError("Username already registered")

        hashed = auth.hash_password(password)
        return crud.create_user(db, username, hashed)

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> str:
        user = crud.get_user_by_username(db, username)
        hashed_password = getattr(user, "hashed_password", None)
        if not user or not hashed_password or not auth.verify_password(password, hashed_password):
            raise ValueError("Invalid credentials")

        return auth.create_access_token({"sub": user.username})
