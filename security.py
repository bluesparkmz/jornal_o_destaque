from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from jose import JWTError, jwt
from pwdlib import PasswordHash
from config import settings
password_hash=PasswordHash.recommended()
def hash_password(value:str)->str: return password_hash.hash(value)
def verify_password(value:str,digest:str|None)->bool: return bool(digest) and password_hash.verify(value,digest)
def create_token(subject:int,kind:str,lifetime:timedelta)->str:
    cfg=settings(); now=datetime.now(timezone.utc)
    return jwt.encode({"sub":str(subject),"type":kind,"iat":now,"exp":now+lifetime},cfg.jwt_secret_key,algorithm=cfg.jwt_algorithm)
def read_token(token:str,kind:str)->int:
    try:
        payload=jwt.decode(token,settings().jwt_secret_key,algorithms=[settings().jwt_algorithm])
        if payload.get("type")!=kind: raise JWTError()
        return int(payload["sub"])
    except (JWTError,KeyError,ValueError) as exc: raise HTTPException(status.HTTP_401_UNAUTHORIZED,"Token inválido ou expirado") from exc
