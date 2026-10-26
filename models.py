from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    String,
    Text,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    Table,
    Column,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


# =========================================================
# TABELAS DE RELACIONAMENTO
# =========================================================

article_categories = Table(
    "article_categories",
    Base.metadata,
    Column(
        "article_id",
        ForeignKey("articles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "category_id",
        ForeignKey("categories.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

article_tags = Table(
    "article_tags",
    Base.metadata,
    Column(
        "article_id",
        ForeignKey("articles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


# =========================================================
# UTILIZADORES
# =========================================================

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    legacy_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        unique=True,
        nullable=True,
    )

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
    )

    display_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    password_hash: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    role: Mapped[str] = mapped_column(
        String(50),
        default="author",
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    articles: Mapped[List["Article"]] = relationship(
        back_populates="author",
    )


# =========================================================
# ARTIGOS / NOTÍCIAS
# =========================================================

class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    legacy_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        unique=True,
        nullable=True,
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        index=True,
        nullable=False,
    )

    excerpt: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    content_format: Mapped[str] = mapped_column(
        String(20),
        default="html",
        nullable=False,
    )

    content_type: Mapped[str] = mapped_column(
        String(50),
        default="post",
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="draft",
        nullable=False,
        index=True,
    )

    comment_status: Mapped[str] = mapped_column(
        String(20),
        default="closed",
        nullable=False,
    )

    views_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        index=True,
    )

    author_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    featured_image_url: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
    )

    source_url: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
    )

    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    author: Mapped[Optional["User"]] = relationship(
        back_populates="articles",
    )

    categories: Mapped[List["Category"]] = relationship(
        secondary=article_categories,
        back_populates="articles",
    )

    tags: Mapped[List["Tag"]] = relationship(
        secondary=article_tags,
        back_populates="articles",
    )

    media: Mapped[List["Media"]] = relationship(
        back_populates="article",
        cascade="all, delete-orphan",
    )

    comments: Mapped[List["Comment"]] = relationship(
        back_populates="article",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index(
            "ix_articles_status_published",
            "status",
            "published_at",
        ),
    )


# =========================================================
# CATEGORIAS
# =========================================================

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    legacy_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        unique=True,
        nullable=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )

    parent: Mapped[Optional["Category"]] = relationship(
        remote_side="Category.id",
        back_populates="children",
    )

    children: Mapped[List["Category"]] = relationship(
        back_populates="parent",
    )

    articles: Mapped[List["Article"]] = relationship(
        secondary=article_categories,
        back_populates="categories",
    )


# =========================================================
# ETIQUETAS
# =========================================================

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    legacy_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        unique=True,
        nullable=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    articles: Mapped[List["Article"]] = relationship(
        secondary=article_tags,
        back_populates="tags",
    )


# =========================================================
# FICHEIROS E IMAGENS
# =========================================================

class Media(Base):
    __tablename__ = "media"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    legacy_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        unique=True,
        nullable=True,
    )

    article_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("articles.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    original_name: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    file_path: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
    )

    url: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
    )

    mime_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    alt_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    article: Mapped[Optional["Article"]] = relationship(
        back_populates="media",
    )


# =========================================================
# COMENTÁRIOS
# =========================================================

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    legacy_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        unique=True,
        nullable=True,
    )

    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    author_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    author_email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    author_url: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
    )

    body: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    article: Mapped["Article"] = relationship(
        back_populates="comments",
    )


# =========================================================
# GOSTOS / LIKES DE NOTÍCIAS
# =========================================================

class ArticleLike(Base):
    __tablename__ = "article_likes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("article_id", "user_id", name="uq_article_like_user"),
    )


# =========================================================
# VISUALIZAÇÕES DE NOTÍCIAS
# =========================================================

class ArticleView(Base):
    __tablename__ = "article_views"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    visitor_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    viewed_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "article_id",
            "visitor_hash",
            "viewed_date",
            name="uq_article_view_visitor_day",
        ),
    )


# =========================================================
# JORNAIS DIGITAIS E COMPRAS
# =========================================================

class Newspaper(Base):
    __tablename__ = "newspapers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    issue_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    cover_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    pdf_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="MZN", nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    purchases: Mapped[List["NewspaperPurchase"]] = relationship(
        back_populates="newspaper", cascade="all, delete-orphan"
    )


class NewspaperPurchase(Base):
    __tablename__ = "newspaper_purchases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    newspaper_id: Mapped[int] = mapped_column(ForeignKey("newspapers.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)
    provider_reference: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    newspaper: Mapped["Newspaper"] = relationship(back_populates="purchases")

    __table_args__ = (
        UniqueConstraint("newspaper_id", "user_id", name="uq_newspaper_purchase_user"),
    )


# =========================================================
# SUBSCRITORES DA NEWSLETTER
# =========================================================

class Subscriber(Base):
    __tablename__ = "subscribers"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    legacy_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        unique=True,
        nullable=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    subscribed_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


# =========================================================
# CONFIGURAÇÕES DA APLICAÇÃO
# =========================================================

class AppSetting(Base):
    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    key: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    value: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
