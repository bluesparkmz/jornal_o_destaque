from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models import Article, ArticleLike, Comment, User


def add_comment(db: Session, article_id: int, body: str, user: User) -> Comment:
    article = db.scalar(
        select(Article).where(Article.id == article_id, Article.status == "published")
    )
    if article is None:
        raise HTTPException(404, "Notícia não encontrada")

    comment = Comment(
        article_id=article.id,
        user_id=user.id,
        author_name=user.display_name or user.username,
        author_email=user.email,
        body=body,
        status="pending",
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def toggle_like(db: Session, article_id: int, user: User) -> bool:
    article = db.scalar(
        select(Article).where(Article.id == article_id, Article.status == "published")
    )
    if article is None:
        raise HTTPException(404, "Notícia não encontrada")

    like = db.scalar(
        select(ArticleLike).where(
            ArticleLike.article_id == article_id,
            ArticleLike.user_id == user.id,
        )
    )
    if like:
        db.delete(like)
        db.commit()
        return False

    db.add(ArticleLike(article_id=article_id, user_id=user.id))
    db.commit()
    return True


def like_count(db: Session, article_id: int) -> int:
    return db.scalar(
        select(func.count(ArticleLike.id)).where(ArticleLike.article_id == article_id)
    ) or 0
