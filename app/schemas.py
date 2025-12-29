from pydantic import BaseModel
from typing import List

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class RoleAssign(BaseModel):
    username: str
    role: str

class PermissionCheck(BaseModel):
    username: str
    resource: str
    action: str

class UserOut(BaseModel):
    id: int
    username: str
    roles: List[str] = []

    class Config:
        orm_mode = True
