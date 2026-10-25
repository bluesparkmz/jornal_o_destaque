from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from database import get_db
from models import Category, Tag
from routers.dependencies import allow
from schemas import CategoryIn, CategoryOut, TagIn, TagOut
router=APIRouter(tags=["Categorias e etiquetas"])
def crud(model,data,db,id=None):
    if db.scalar(select(model).where(model.slug==data.slug, model.id != (id or 0))): raise HTTPException(409,"Slug já existe")
    item=db.get(model,id) if id else model()
    if not item: raise HTTPException(404,"Recurso não encontrado")
    for key,value in data.model_dump().items(): setattr(item,key,value)
    db.add(item); db.commit(); db.refresh(item); return item
@router.get("/categories",response_model=list[CategoryOut])
def categories(db:Session=Depends(get_db)): return list(db.scalars(select(Category).order_by(Category.name)))
@router.get("/categories/{slug}",response_model=CategoryOut)
def category(slug:str,db:Session=Depends(get_db)):
    item=db.scalar(select(Category).where(Category.slug==slug))
    if not item: raise HTTPException(404,"Categoria não encontrada")
    return item
@router.post("/categories",response_model=CategoryOut,status_code=201)
def new_category(data:CategoryIn,db:Session=Depends(get_db),_=Depends(allow("admin","editor"))): return crud(Category,data,db)
@router.put("/categories/{item_id}",response_model=CategoryOut)
def edit_category(item_id:int,data:CategoryIn,db:Session=Depends(get_db),_=Depends(allow("admin","editor"))): return crud(Category,data,db,item_id)
@router.delete("/categories/{item_id}",status_code=204)
def remove_category(item_id:int,db:Session=Depends(get_db),_=Depends(allow("admin","editor"))):
    item=db.get(Category,item_id)
    if not item: raise HTTPException(404,"Categoria não encontrada")
    db.delete(item);db.commit()
@router.get("/tags",response_model=list[TagOut])
def tags(db:Session=Depends(get_db)): return list(db.scalars(select(Tag).order_by(Tag.name)))
@router.post("/tags",response_model=TagOut,status_code=201)
def new_tag(data:TagIn,db:Session=Depends(get_db),_=Depends(allow("admin","editor"))): return crud(Tag,data,db)
@router.put("/tags/{item_id}",response_model=TagOut)
def edit_tag(item_id:int,data:TagIn,db:Session=Depends(get_db),_=Depends(allow("admin","editor"))): return crud(Tag,data,db,item_id)
