from datetime import datetime, timezone
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from config import settings

from controllers.newspaper_controller import (
    can_download,
    create_newspaper,
    list_user_purchases,
    purchase_newspaper,
    save_pdf,
    update_purchase_status,
)
from controllers.media_controller import save_newspaper_cover
from controllers.storage_controller import create_private_pdf_upload, download_private, private_pdf_size
from controllers.skywallet_controller import create_payment, payment_status
from database import get_db
from models import Newspaper, NewspaperPurchase, User
from routers.dependencies import allow, current_user
from schemas import DirectPdfUploadOut, NewspaperDirectIn, NewspaperOut, PaymentRequestIn, PurchaseOut

router = APIRouter(prefix="/newspapers", tags=["Jornais digitais"])


@router.get("", response_model=list[NewspaperOut])
def list_newspapers(db: Session = Depends(get_db)):
    return list(db.scalars(select(Newspaper).where(Newspaper.is_published.is_(True)).order_by(Newspaper.published_at.desc())))


@router.get("/my-purchases", response_model=list[PurchaseOut])
def my_purchases(
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    return list_user_purchases(db, user)


@router.get("/{slug}", response_model=NewspaperOut)
def newspaper(slug: str, db: Session = Depends(get_db)):
    item = db.scalar(select(Newspaper).where(Newspaper.slug == slug, Newspaper.is_published.is_(True)))
    if not item:
        raise HTTPException(404, "Jornal não encontrado.")
    return item


@router.post("/upload", response_model=NewspaperOut, status_code=201)
async def upload_newspaper(
    title: str = Form(...),
    price_cents: int = Form(...),
    pdf: UploadFile = File(...),
    description: str | None = Form(default=None),
    issue_number: str | None = Form(default=None),
    cover_image: UploadFile = File(...),
    is_published: bool = Form(default=False),
    db: Session = Depends(get_db),
    _: User = Depends(allow("admin", "editor")),
):
    path = await save_pdf(pdf)
    cover_url = await save_newspaper_cover(cover_image)
    item = Newspaper(
        title=title,
        slug=title,
        description=description,
        issue_number=issue_number,
        cover_url=cover_url,
        pdf_path=path,
        price_cents=price_cents,
        is_published=is_published,
    )
    return create_newspaper(db, item)


@router.post("/pdf-upload-url", response_model=DirectPdfUploadOut)
def pdf_upload_url(_: User = Depends(allow("admin", "editor"))):
    key, upload_url = create_private_pdf_upload()
    return DirectPdfUploadOut(key=key, upload_url=upload_url, headers={"Content-Type": "application/pdf"})


@router.post("/direct", response_model=NewspaperOut, status_code=201)
def create_uploaded_newspaper(
    data: NewspaperDirectIn,
    db: Session = Depends(get_db),
    _: User = Depends(allow("admin", "editor")),
):
    size = private_pdf_size(data.pdf_key)
    if size < 5:
        raise HTTPException(422, "O PDF enviado está vazio.")
    if size > settings().max_newspaper_pdf_bytes:
        raise HTTPException(413, "O PDF excede o limite permitido.")
    return create_newspaper(db, Newspaper(
        title=data.title,
        slug=data.title,
        description=data.description,
        issue_number=data.issue_number,
        cover_url=data.cover_url,
        pdf_path=data.pdf_key,
        price_cents=data.price_cents,
        is_published=data.is_published,
    ))


@router.post("/{newspaper_id}/purchase", response_model=PurchaseOut, status_code=201)
def purchase(newspaper_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = db.get(Newspaper, newspaper_id)
    if not item or not item.is_published:
        raise HTTPException(404, "Jornal não encontrado.")
    return purchase_newspaper(db, item, user)


@router.post("/purchases/{purchase_id}/pay", response_model=PurchaseOut)
def pay(
    purchase_id: int,
    data: PaymentRequestIn,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    purchase = db.get(NewspaperPurchase, purchase_id)
    if not purchase or purchase.user_id != user.id:
        raise HTTPException(404, "Compra não encontrada.")
    if purchase.status == "paid":
        return purchase
    newspaper = db.get(Newspaper, purchase.newspaper_id)
    purchase.provider_reference = create_payment(
        data.msisdn,
        purchase.amount_cents,
        f"Jornal O Destaque: {newspaper.title}",
    )
    purchase.status = "pending"
    db.commit()
    db.refresh(purchase)
    return purchase


@router.get("/purchases/{purchase_id}", response_model=PurchaseOut)
def purchase_status(
    purchase_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    purchase = db.get(NewspaperPurchase, purchase_id)
    if not purchase or purchase.user_id != user.id:
        raise HTTPException(404, "Compra não encontrada.")
    if purchase.status == "pending" and purchase.provider_reference:
        update_purchase_status(purchase, payment_status(purchase.provider_reference))
        db.commit()
        db.refresh(purchase)
    return purchase


@router.get("/{newspaper_id}/download")
def download(newspaper_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = can_download(db, newspaper_id, user)
    object_data = download_private(item.pdf_path)
    return StreamingResponse(
        object_data["Body"].iter_chunks(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{item.slug}.pdf"'},
    )
