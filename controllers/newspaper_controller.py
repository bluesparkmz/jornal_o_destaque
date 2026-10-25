from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from config import settings
from models import Newspaper, NewspaperPurchase, User


async def save_pdf(pdf: UploadFile) -> str:
    if pdf.content_type not in {"application/pdf", "application/x-pdf"}:
        raise HTTPException(415, "Envie apenas ficheiros PDF.")

    content = await pdf.read()
    if not content.startswith(b"%PDF-"):
        raise HTTPException(415, "O conteúdo do ficheiro não é um PDF válido.")
    if len(content) > settings().max_upload_bytes:
        raise HTTPException(413, "O PDF excede o limite de tamanho configurado.")

    directory = settings().upload_dir / "newspapers"
    directory.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}.pdf"
    path = directory / filename
    path.write_bytes(content)
    return str(path)


def create_newspaper(db: Session, newspaper: Newspaper) -> Newspaper:
    if db.scalar(select(Newspaper).where(Newspaper.slug == newspaper.slug)):
        raise HTTPException(409, "Já existe um jornal com este slug.")
    if newspaper.price_cents < 0:
        raise HTTPException(422, "O preço não pode ser negativo.")
    if newspaper.is_published:
        newspaper.published_at = datetime.now(timezone.utc)
    db.add(newspaper)
    db.commit()
    db.refresh(newspaper)
    return newspaper


def purchase_newspaper(db: Session, newspaper: Newspaper, user: User) -> NewspaperPurchase:
    previous = db.scalar(
        select(NewspaperPurchase).where(
            NewspaperPurchase.newspaper_id == newspaper.id,
            NewspaperPurchase.user_id == user.id,
        )
    )
    if previous:
        return previous

    purchase = NewspaperPurchase(
        newspaper_id=newspaper.id,
        user_id=user.id,
        amount_cents=newspaper.price_cents,
        currency=newspaper.currency,
        status="paid" if newspaper.price_cents == 0 else "pending",
        paid_at=datetime.now(timezone.utc) if newspaper.price_cents == 0 else None,
    )
    db.add(purchase)
    db.commit()
    db.refresh(purchase)
    return purchase


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
