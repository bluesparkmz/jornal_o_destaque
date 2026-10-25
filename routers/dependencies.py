from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from database import get_db
from models import User
from security import read_token
bearer=HTTPBearer(auto_error=False)
def current_user(credentials:HTTPAuthorizationCredentials|None=Depends(bearer),db:Session=Depends(get_db)):
    if not credentials: raise HTTPException(status.HTTP_401_UNAUTHORIZED,"Autenticação necessária")
    user=db.get(User,read_token(credentials.credentials,"access"))
    if not user or not user.is_active: raise HTTPException(status.HTTP_401_UNAUTHORIZED,"Utilizador inválido")
    return user
def allow(*roles):
    def guard(user:User=Depends(current_user)):
        if user.role not in roles: raise HTTPException(status.HTTP_403_FORBIDDEN,"Permissão insuficiente")
        return user
    return guard
