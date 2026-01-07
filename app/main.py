from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.core.openapi import setup_openapi
from app.core.security import get_current_user
from app import schemas, models
from app.core.tags import TAGS_METADATA
from app.services.auth_service import AuthService
from app.services.permission_service import PermissionService
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI(
    title="AccessGuard",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
    openapi_tags=TAGS_METADATA,
)

# Setup custom OpenAPI for Swagger JWT
setup_openapi(app)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# -----------------------
# Redoc endpoint
# -----------------------

@app.get("/redoc", include_in_schema=False)
def redoc():
    return HTMLResponse("""
<!DOCTYPE html>
<html>
  <head>
    <title>AccessGuard API – Redoc</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      body { margin: 0; padding: 0; }
    </style>
  </head>
  <body>
    <redoc spec-url="/openapi.json"></redoc>
    <script src="/static/redoc.standalone.js"></script>
  </body>
</html>
""")

# -----------------------
# Authentication endpoints
# -----------------------

@app.post("/auth/register", response_model=schemas.UserOut, tags=["Authentication"])
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        user = AuthService.register_user(db, user_in.username, user_in.password)
        return schemas.UserOut.from_orm(user)
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.post("/auth/login", response_model=schemas.Token, tags=["Authentication"])
def login(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        token = AuthService.authenticate_user(db, user_in.username, user_in.password)
        return schemas.Token(access_token=token)
    except ValueError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=str(e))

# -----------------------
# Roles & Permissions endpoints
# -----------------------

@app.post("/roles/assign", tags=["Roles"])
def assign_role(
    payload: schemas.RoleAssign,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        user = PermissionService.assign_role(db, payload.username, payload.role)
        return {
            "username": user.username,
            "roles": [r.name for r in user.roles],
        }
    except ValueError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))

@app.post("/permissions/create", tags=["Permissions"])
def create_permission(
    payload: schemas.PermissionCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    role, perm = PermissionService.create_permission_for_role(
        db, payload.resource, payload.action, payload.role_name
    )
    return {
        "role": role.name,
        "permission": {"resource": perm.resource, "action": perm.action},
    }

@app.post("/permissions/check", tags=["Permissions"])
def check_permission(
    payload: schemas.PermissionCheck,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    allowed = PermissionService.check_user_permission(
        db,
        current_user,
        payload.resource,
        payload.action,
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    return {"allowed": True}
