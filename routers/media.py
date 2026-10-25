from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from controllers.media_controller import upload_image
from database import get_db
from models import User
from routers.dependencies import allow
from schemas import MediaOut

router = APIRouter(prefix="/media", tags=["Multimédia"])


@router.post("/upload", response_model=MediaOut, status_code=201)
async def upload(
    image: UploadFile = File(...),
    alt_text: str | None = Form(default=None),
    article_id: int | None = Form(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(allow("admin", "editor", "author")),
):
    return await upload_image(db, image, alt_text, article_id)
