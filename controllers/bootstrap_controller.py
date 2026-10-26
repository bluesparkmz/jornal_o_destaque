from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from config import settings
from models import User
from security import hash_password


def create_initial_admin(db: Session) -> bool:
    """Cria apenas o primeiro admin configurado por ambiente; nunca altera um existente."""
    cfg = settings()
    if not cfg.admin_email or not cfg.admin_password:
        return False
    if len(cfg.admin_password) < 10:
        raise RuntimeError("ADMIN_PASSWORD deve ter pelo menos 10 caracteres.")

    exists = db.scalar(
        select(User).where(
            or_(User.email == cfg.admin_email, User.username == cfg.admin_username)
        )
    )
    if exists:
        return False

    admin = User(
        username=cfg.admin_username,
        email=cfg.admin_email,
        display_name="Administrador",
        password_hash=hash_password(cfg.admin_password),
        role="admin",
        is_active=True,
    )
    db.add(admin)
    db.commit()
    return True
