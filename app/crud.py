from sqlalchemy.orm import Session
from . import models

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, username: str, hashed_password: str):
    user = models.User(username=username, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_or_create_role(db: Session, name: str):
    role = db.query(models.Role).filter(models.Role.name == name).first()
    if not role:
        role = models.Role(name=name)
        db.add(role)
        db.commit()
        db.refresh(role)
    return role

def assign_role_to_user(db: Session, user: models.User, role: models.Role):
    if role not in user.roles:
        user.roles.append(role)
        db.commit()
        db.refresh(user)
    return user

def check_permission(db: Session, username: str, resource: str, action: str) -> bool:
    user = get_user_by_username(db, username)
    if not user:
        return False
    for role in user.roles:
        for p in role.permissions:
            if p.resource == resource and p.action == action:
                return True
    return False

def create_permission(db: Session, resource: str, action: str):
    perm = db.query(models.Permission).filter(
        models.Permission.resource == resource,
        models.Permission.action == action
    ).first()
    if not perm:
        perm = models.Permission(resource=resource, action=action)
        db.add(perm)
        db.commit()
        db.refresh(perm)
    return perm

def add_permission_to_role(db: Session, role: models.Role, permission: models.Permission):
    if permission not in role.permissions:
        role.permissions.append(permission)
        db.commit()
        db.refresh(role)
    return role
