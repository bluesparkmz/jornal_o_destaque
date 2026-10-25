from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from controllers.auth_controller import login, register, tokens
from database import get_db
from models import User
from routers.dependencies import current_user
from schemas import LoginIn, RefreshIn, RegisterIn, TokenOut, UserOut, Message
from security import read_token
router=APIRouter(prefix="/auth",tags=["Autenticação"])
@router.post("/register",response_model=UserOut,status_code=201)
def signup(data:RegisterIn,db:Session=Depends(get_db)): return register(db,data)
@router.post("/login",response_model=TokenOut)
def signin(data:LoginIn,db:Session=Depends(get_db)): return login(db,data)
@router.post("/refresh",response_model=TokenOut)
def refresh(data:RefreshIn,db:Session=Depends(get_db)):
    user=db.get(User,read_token(data.refresh_token,"refresh"))
    if not user or not user.is_active: from fastapi import HTTPException; raise HTTPException(401,"Token inválido")
    return tokens(user)
@router.get("/me",response_model=UserOut)
def me(user:User=Depends(current_user)): return user
@router.post("/logout",response_model=Message)
def logout(user:User=Depends(current_user)): return {"message":"Termine a sessão removendo os tokens no cliente."}
