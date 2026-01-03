from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import schemas
from .database import engine, Base, get_db
from app.services.auth_service import AuthService
from app.services.permission_service import PermissionService

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AccessGuard MVP")

@app.post("/auth/register", response_model=schemas.UserOut)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        user = AuthService.register_user(db, user_in.username, user_in.password)
        return schemas.UserOut.from_orm(user)
    except ValueError as e:
        raise HTTPException(400, str(e))

@app.post("/auth/login", response_model=schemas.Token)
def login(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        token = AuthService.authenticate_user(db, user_in.username, user_in.password)
        return schemas.Token(access_token=token)
    except ValueError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e))

@app.post("/roles/assign")
def assign_role(payload: schemas.RoleAssign, db: Session = Depends(get_db)):
    try:
        user = PermissionService.assign_role(
            db, payload.username, payload.role
        )
        return {
            "username": user.username,
            "roles": [r.name for r in user.roles],
        }
    except ValueError as e:
        raise HTTPException(404, str(e))

@app.post("/permissions/create")
def create_permission(
    resource: str,
    action: str,
    role_name: str,
    db: Session = Depends(get_db),
):
    role, perm = PermissionService.create_permission_for_role(
        db, resource, action, role_name
    )
    return {
        "role": role.name,
        "permission": {"resource": perm.resource, "action": perm.action},
    }

@app.post("/permissions/check")
def check_permission(
    payload: schemas.PermissionCheck,
    db: Session = Depends(get_db),
):
    allowed = PermissionService.check_user_permission(
        db, payload.username, payload.resource, payload.action
    )
    return {"allowed": allowed}
