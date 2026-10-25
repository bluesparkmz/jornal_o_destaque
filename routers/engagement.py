from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from controllers.engagement_controller import add_comment, like_count, toggle_like
from database import get_db
from models import Comment, User
from routers.dependencies import current_user
from schemas import CommentIn, CommentOut, Message

router = APIRouter(prefix="/articles", tags=["Interações"])


@router.post("/{article_id}/comments", response_model=Message, status_code=201)
def create_comment(
    article_id: int,
    data: CommentIn,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    add_comment(db, article_id, data.body, user)
    return {"message": "Comentário enviado para moderação."}


@router.get("/{article_id}/comments", response_model=list[CommentOut])
def comments(article_id: int, db: Session = Depends(get_db)):
    return list(
        db.scalars(
            select(Comment).where(
                Comment.article_id == article_id,
                Comment.status == "approved",
            ).order_by(Comment.created_at.desc())
        )
    )


@router.post("/{article_id}/like")
def like(
    article_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    liked = toggle_like(db, article_id, user)
    return {"liked": liked, "likes": like_count(db, article_id)}


@router.get("/{article_id}/likes")
def likes(article_id: int, db: Session = Depends(get_db)):
    return {"likes": like_count(db, article_id)}
