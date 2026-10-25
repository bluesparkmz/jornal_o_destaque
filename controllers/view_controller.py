from datetime import datetime, timezone
from hashlib import sha256

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import Article, ArticleView


def register_view(db: Session, article: Article, client_ip: str, user_agent: str) -> int:
    """Conta no máximo uma visualização por visitante e por dia."""
    day = datetime.now(timezone.utc).date().isoformat()
    fingerprint = sha256(f"{client_ip}|{user_agent}".encode()).hexdigest()
    view = ArticleView(
        article_id=article.id,
        visitor_hash=fingerprint,
        viewed_date=datetime.fromisoformat(day),
    )
    try:
        db.add(view)
        db.flush()
    except IntegrityError:
        db.rollback()
        db.refresh(article)
        return article.views_count

    article.views_count += 1
    db.commit()
    return article.views_count
