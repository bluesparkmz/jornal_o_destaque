from datetime import datetime, timezone
import re
import unicodedata
from uuid import uuid4
import secrets

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from config import settings
from controllers.storage_controller import upload_bytes
from models import Newspaper, NewspaperPurchase, User


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")
    if not slug:
        raise HTTPException(422, "Não foi possível gerar um slug a partir do título.")
    return slug[:255]


async def save_pdf(pdf: UploadFile) -> str:
    if pdf.content_type not in {"application/pdf", "application/x-pdf"}:
        raise HTTPException(415, "Envie apenas ficheiros PDF.")

    content = await pdf.read()
    if not content.startswith(b"%PDF-"):
        raise HTTPException(415, "O conteúdo do ficheiro não é um PDF válido.")
    if len(content) > settings().max_upload_bytes:
        raise HTTPException(413, "O PDF excede o limite de tamanho configurado.")

    filename = f"{uuid4().hex}.pdf"
    return upload_bytes(f"newspapers/{filename}", content, "application/pdf", public=False)


def create_newspaper(db: Session, newspaper: Newspaper) -> Newspaper:
    base_slug = slugify(newspaper.slug or newspaper.title)
    slug = base_slug
    suffix = 2
    while db.scalar(select(Newspaper.id).where(Newspaper.slug == slug)):
        slug = f"{base_slug[:250]}-{suffix}"
        suffix += 1
    newspaper.slug = slug
    if newspaper.price < 0:
        raise HTTPException(422, "O preço não pode ser negativo.")
    if newspaper.is_published:
        newspaper.published_at = datetime.now(timezone.utc)
    db.add(newspaper)
    db.commit()
    db.refresh(newspaper)
    return newspaper


def purchase_newspaper(db: Session, newspaper: Newspaper, user: User | None, guest_name: str | None = None, guest_email: str | None = None) -> NewspaperPurchase:
    if user is None and not guest_email:
        raise HTTPException(422, "Indique o nome e e-mail para continuar sem conta.")
    if user is None:
        purchase = NewspaperPurchase(newspaper_id=newspaper.id, user_id=None, guest_name=guest_name, guest_email=guest_email, checkout_token=secrets.token_urlsafe(32), amount=newspaper.price, currency=newspaper.currency, status="paid" if newspaper.price == 0 else "pending", paid_at=datetime.now(timezone.utc) if newspaper.price == 0 else None)
        db.add(purchase); db.commit(); db.refresh(purchase); return purchase
    previous = db.scalar(
        select(NewspaperPurchase).where(
            NewspaperPurchase.newspaper_id == newspaper.id,
            NewspaperPurchase.user_id == user.id,
        )
    )
    if previous:
        if not previous.checkout_token:
            previous.checkout_token = secrets.token_urlsafe(32)
            db.commit(); db.refresh(previous)
        return previous

    purchase = NewspaperPurchase(
        newspaper_id=newspaper.id,
        user_id=user.id,
        checkout_token=secrets.token_urlsafe(32),
        amount=newspaper.price,
        currency=newspaper.currency,
        status="paid" if newspaper.price == 0 else "pending",
        paid_at=datetime.now(timezone.utc) if newspaper.price == 0 else None,
    )
    db.add(purchase)
    db.commit()
    db.refresh(purchase)
    return purchase


def purchase_allowed(purchase: NewspaperPurchase, user: User | None, checkout_token: str | None) -> bool:
    return bool((user and (user.role == "admin" or purchase.user_id == user.id)) or (checkout_token and secrets.compare_digest(purchase.checkout_token or "", checkout_token)))


def update_purchase_status(purchase: NewspaperPurchase, provider_status: str) -> None:
    if provider_status == "success":
        purchase.status = "paid"
        purchase.paid_at = datetime.now(timezone.utc)
    elif provider_status == "failed":
        purchase.status = "failed"


def can_download(db: Session, newspaper_id: int, user: User) -> Newspaper:
    newspaper = db.get(Newspaper, newspaper_id)
    if not newspaper or not newspaper.is_published:
        raise HTTPException(404, "Jornal não encontrado.")
    if user.role == "admin":
        return newspaper
    purchase = db.scalar(
        select(NewspaperPurchase).where(
            NewspaperPurchase.newspaper_id == newspaper_id,
            NewspaperPurchase.user_id == user.id,
            NewspaperPurchase.status == "paid",
        )
    )
    if not purchase:
        raise HTTPException(403, "É necessária uma compra paga para descarregar este jornal.")
    return newspaper


def list_user_purchases(db: Session, user: User) -> list[NewspaperPurchase]:
    return list(
        db.scalars(
            select(NewspaperPurchase)
            .where(NewspaperPurchase.user_id == user.id)
            .order_by(NewspaperPurchase.created_at.desc())
        )
    )
