from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.orm import Session
from controllers.article_controller import assign, create, get_article, list_articles, query_public
from controllers.view_controller import register_view
from database import get_db
from models import Article, User
from routers.dependencies import allow, current_user
from schemas import ArticleIn, ArticleOut, ArticlePage, ArticlePatch
router=APIRouter(prefix="/articles",tags=["Notícias"])
@router.get("",response_model=ArticlePage)
def listing(page:int=Query(1,ge=1),per_page:int=Query(20,ge=1,le=100),q:str|None=None,category:str|None=None,tag:str|None=None,author_id:int|None=None,sort:str=Query("published_at",pattern="^(published_at|title|created_at)$"),order:str=Query("desc",pattern="^(asc|desc)$"),db:Session=Depends(get_db)):
    items,total=list_articles(db,page,per_page,q,category,tag,author_id,sort,order); return {"items":items,"page":page,"per_page":per_page,"total":total}
@router.get("/latest",response_model=list[ArticleOut])
def latest(db:Session=Depends(get_db)): return list_articles(db,1,10,sort="published_at")[0]
@router.get("/featured",response_model=list[ArticleOut])
def featured(db:Session=Depends(get_db)): return list_articles(db,1,10,category="destaque")[0]
@router.get("/search",response_model=ArticlePage)
def search(q:str=Query(min_length=2,max_length=150),page:int=Query(1,ge=1),per_page:int=Query(20,ge=1,le=100),db:Session=Depends(get_db)):
    items,total=list_articles(db,page,per_page,q=q); return {"items":items,"page":page,"per_page":per_page,"total":total}
@router.get("/slug/{slug}",response_model=ArticleOut)
def by_slug(slug:str,request:Request,db:Session=Depends(get_db)):
    item=db.scalar(query_public().where(Article.slug==slug))
    if not item: raise HTTPException(404,"Notícia não encontrada")
    register_view(db, item, request.client.host if request.client else "unknown", request.headers.get("user-agent", ""))
    return item
@router.get("/{article_id}",response_model=ArticleOut)
def detail(article_id:int,request:Request,db:Session=Depends(get_db)):
    item=get_article(db,article_id)
    register_view(db, item, request.client.host if request.client else "unknown", request.headers.get("user-agent", ""))
    return item
@router.post("",response_model=ArticleOut,status_code=201)
def add(data:ArticleIn,db:Session=Depends(get_db),user:User=Depends(allow("admin","editor","author"))): return create(db,data,user)
@router.patch("/{article_id}",response_model=ArticleOut)
@router.put("/{article_id}",response_model=ArticleOut)
def edit(article_id:int,data:ArticlePatch,db:Session=Depends(get_db),user:User=Depends(allow("admin","editor","author"))):
    item=get_article(db,article_id,False)
    if user.role=="author" and item.author_id!=user.id: raise HTTPException(403,"Só pode editar as suas notícias")
    assign(db,item,data); db.commit(); return get_article(db,article_id,False)
@router.delete("/{article_id}",status_code=204)
def delete(article_id:int,db:Session=Depends(get_db),user:User=Depends(allow("admin","editor"))): db.delete(get_article(db,article_id,False)); db.commit()
