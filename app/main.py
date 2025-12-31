from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import schemas, crud, auth
from .database import engine, Base, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AccessGuard MVP")

@app.post("/auth/register", response_model=schemas.UserOut)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_username(db, user_in.username)
    if existing:
        raise HTTPException(400, "Username already registered")
    hashed = auth.hash_password(user_in.password)
    user = crud.create_user(db, user_in.username, hashed)
    return schemas.UserOut.from_orm(user)

@app.post("/auth/login", response_model=schemas.Token)
def login(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, user_in.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    hashed_password = getattr(user, "hashed_password", None)
    if not hashed_password or not auth.verify_password(user_in.password, hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = auth.create_access_token({"sub": user.username})
    return schemas.Token(access_token=token)

@app.post("/roles/assign")
def assign_role(payload: schemas.RoleAssign, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, payload.username)
    if not user:
        raise HTTPException(404, "User not found")
    role = crud.get_or_create_role(db, payload.role)
    user = crud.assign_role_to_user(db, user, role)
    return {"username": user.username, "roles": [r.name for r in user.roles]}

@app.post("/permissions/create")
def create_permission(resource: str, action: str, role_name: str, db: Session = Depends(get_db)):
    role = crud.get_or_create_role(db, role_name)
    perm = crud.create_permission(db, resource, action)
    crud.add_permission_to_role(db, role, perm)
    return {"role": role.name, "permission": {"resource": resource, "action": action}}

@app.post("/permissions/check")
def check_permission(payload: schemas.PermissionCheck, db: Session = Depends(get_db)):
    allowed = crud.check_permission(db, payload.username, payload.resource, payload.action)
    return {"allowed": allowed}
