from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from config import settings
from models import User
from schemas import LoginIn, RegisterIn, TokenOut
from security import create_token, hash_password, verify_password

def tokens(user: User) -> TokenOut:
    cfg = settings()
    return TokenOut(access_token=create_token(user.id,"access",timedelta(minutes=cfg.access_token_minutes)), refresh_token=create_token(user.id,"refresh",timedelta(days=cfg.refresh_token_days)))
def register(db: Session, data: RegisterIn) -> User:
    if db.scalar(select(User).where(or_(User.email == data.email, User.username == data.username))): raise HTTPException(status.HTTP_409_CONFLICT,"Email ou utilizador já existe")
    user=User(username=data.username,email=str(data.email),display_name=data.display_name,password_hash=hash_password(data.password),role="reader")
    db.add(user); db.commit(); db.refresh(user); return user
def login(db: Session, data: LoginIn) -> TokenOut:
    user=db.scalar(select(User).where(or_(User.email==data.identity,User.username==data.identity)))
    if not user or not user.is_active or not verify_password(data.password,user.password_hash): raise HTTPException(status.HTTP_401_UNAUTHORIZED,"Credenciais inválidas")
    return tokens(user)
