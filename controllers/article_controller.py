from datetime import datetime, timezone
import re
import unicodedata
from fastapi import HTTPException, status
from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import Session, selectinload
from models import Article, Category, Tag, User
from schemas import ArticleIn, ArticlePatch

LOAD=(selectinload(Article.author),selectinload(Article.categories),selectinload(Article.tags))
def query_public(): return select(Article).options(*LOAD).where(Article.status=="published")
def unique_slug(db: Session, title: str) -> str:
    value = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode().lower()
    base = re.sub(r"[^a-z0-9]+", "-", value).strip("-")[:490]
    if not base: raise HTTPException(422, "Não foi possível gerar um slug a partir do título")
    slug, suffix = base, 2
    while db.scalar(select(Article.id).where(Article.slug == slug)):
        slug = f"{base[:490-len(str(suffix))]}-{suffix}"
        suffix += 1
    return slug
def first_markdown_image(content: str) -> str | None:
    match = re.search(r"!\[[^\]]*\]\(([^\s)]+)", content)
    return match.group(1) if match else None
def apply_missing_covers(articles: list[Article]) -> None:
    """Compatibilidade para artigos antigos criados antes da capa existir."""
    for article in articles:
        if not article.featured_image_url:
            article.featured_image_url = first_markdown_image(article.content)
def get_article(db:Session,article_id:int,public=True)->Article:
    query=select(Article).options(*LOAD).where(Article.id==article_id)
    if public: query=query.where(Article.status=="published")
    article=db.scalar(query)
    if not article: raise HTTPException(status.HTTP_404_NOT_FOUND,"Notícia não encontrada")
    return article
def list_articles(db:Session,page:int,per_page:int,q:str|None=None,category:str|None=None,tag:str|None=None,author_id:int|None=None,sort:str="published_at",order:str="desc"):
    stmt=query_public()
    if q: stmt=stmt.where(or_(Article.title.ilike(f"%{q}%"),Article.excerpt.ilike(f"%{q}%"),Article.content.ilike(f"%{q}%")))
    if category: stmt=stmt.join(Article.categories).where(Category.slug==category)
    if tag: stmt=stmt.join(Article.tags).where(Tag.slug==tag)
    if author_id: stmt=stmt.where(Article.author_id==author_id)
    field={"published_at":Article.published_at,"title":Article.title,"created_at":Article.created_at}[sort]
    stmt=stmt.order_by(desc(field) if order=="desc" else asc(field))
    total=db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
    articles = list(db.scalars(stmt.offset((page-1)*per_page).limit(per_page)).unique())
    apply_missing_covers(articles)
    return articles,total
def assign(db:Session,article:Article,data:ArticleIn|ArticlePatch):
    values=data.model_dump(exclude_unset=True,exclude={"category_ids","tag_ids","slug"})
    if "status" in values and values["status"] not in {"draft","pending","published","archived"}: raise HTTPException(422,"Estado inválido")
    for key,value in values.items(): setattr(article,key,value)
    if "content" in values and not article.featured_image_url:
        article.featured_image_url = first_markdown_image(article.content)
    if article.status=="published" and not article.published_at: article.published_at=datetime.now(timezone.utc)
    if data.category_ids is not None: article.categories=list(db.scalars(select(Category).where(Category.id.in_(data.category_ids))).all())
    if data.tag_ids is not None: article.tags=list(db.scalars(select(Tag).where(Tag.id.in_(data.tag_ids))).all())
def create(db:Session,data:ArticleIn,user:User)->Article:
    # O endereço público é sempre derivado do título; ignorar slug do cliente.
    data.slug = None
    if db.scalar(select(Article).where(Article.slug==data.slug)): raise HTTPException(409,"Slug já existe")
    article=Article(author_id=user.id,title=data.title,slug=unique_slug(db,data.title),content=data.content); assign(db,article,data); db.add(article); db.commit(); return get_article(db,article.id,False)
