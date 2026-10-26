from fastapi import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from models import User
from schemas import AdminUserCreate, UserRoleUpdate
from security import hash_password


def list_users(db: Session) -> list[User]:
    return list(db.scalars(select(User).order_by(User.created_at.desc())))


def create_user(db: Session, data: AdminUserCreate) -> User:
    duplicate = db.scalar(
        select(User).where(or_(User.username == data.username, User.email == str(data.email)))
    )
    if duplicate:
        raise HTTPException(409, "Já existe um utilizador com este email ou nome.")
    user = User(
        username=data.username,
        email=str(data.email),
        display_name=data.display_name,
        password_hash=hash_password(data.password),
        role=data.role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, data: UserRoleUpdate, acting_user: User) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "Utilizador não encontrado.")
    if user.id == acting_user.id and (data.role != "admin" or data.is_active is False):
        raise HTTPException(422, "Não pode remover ou desactivar o seu próprio acesso de admin.")
    user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active
    db.commit()
    db.refresh(user)
    return user
