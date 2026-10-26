from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from controllers.admin_controller import create_user, list_users, update_user
from database import get_db
from models import User
from routers.dependencies import allow
from schemas import AdminUserCreate, UserOut, UserRoleUpdate

router = APIRouter(prefix="/admin", tags=["Administração"])


@router.get("/users", response_model=list[UserOut])
def users(
    db: Session = Depends(get_db),
    _: User = Depends(allow("admin")),
):
    return list_users(db)


@router.post("/users", response_model=UserOut, status_code=201)
def add_user(
    data: AdminUserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(allow("admin")),
):
    return create_user(db, data)


@router.patch("/users/{user_id}", response_model=UserOut)
def change_user(
    user_id: int,
    data: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(allow("admin")),
):
    return update_user(db, user_id, data, current_admin)
