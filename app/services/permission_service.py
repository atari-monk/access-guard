from sqlalchemy.orm import Session
from app import crud, models

class PermissionService:
    @staticmethod
    def assign_role(db: Session, username: str, role_name: str) -> models.User:
        user = crud.get_user_by_username(db, username)
        if not user:
            raise ValueError("User not found")

        role = crud.get_or_create_role(db, role_name)
        return crud.assign_role_to_user(db, user, role)

    @staticmethod
    def create_permission_for_role(
        db: Session, resource: str, action: str, role_name: str
    ):
        role = crud.get_or_create_role(db, role_name)
        perm = crud.create_permission(db, resource, action)
        crud.add_permission_to_role(db, role, perm)
        return role, perm

    @staticmethod
    def check_user_permission(
        db: Session,
        user: models.User,
        resource: str,
        action: str,
    ) -> bool:
        for role in user.roles:
            for perm in role.permissions:
                if perm.resource == resource and perm.action == action:
                    return True
        return False