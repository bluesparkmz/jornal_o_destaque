from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from sqlalchemy.orm import Session

from config import settings
from models import Media

ALLOWED_FORMATS = {
    "JPEG",
    "PNG",
    "WEBP",
}


async def upload_image(
    db: Session,
    image: UploadFile,
    alt_text: str | None,
    article_id: int | None,
) -> Media:
    content = await image.read()
    if not content:
        raise HTTPException(422, "A imagem está vazia.")
    if len(content) > settings().max_upload_bytes:
        raise HTTPException(413, "A imagem excede o limite de tamanho.")

    try:
        from io import BytesIO
        with Image.open(BytesIO(content)) as source:
            image_format = source.format
            source.verify()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(415, "Envie uma imagem JPEG, PNG ou WebP válida.")

    if image_format not in ALLOWED_FORMATS:
        raise HTTPException(415, "São permitidas apenas imagens JPEG, PNG e WebP.")

    try:
        with Image.open(BytesIO(content)) as source:
            if getattr(source, "n_frames", 1) > 1:
                raise HTTPException(422, "Imagens animadas não são suportadas no upload editorial.")
    except UnidentifiedImageError:
        raise HTTPException(415, "Envie uma imagem JPEG, PNG ou WebP válida.")

    directory = settings().upload_dir / "media"
    directory.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}.webp"
    path = directory / filename

    try:
        with Image.open(BytesIO(content)) as source:
            # O ficheiro de saída não conserva EXIF/GPS nem outros metadados.
            converted = source.convert("RGBA" if source.mode in {"RGBA", "LA", "P"} else "RGB")
            converted.save(
                path,
                format="WEBP",
                quality=settings().image_webp_quality,
                method=6,
            )
    except OSError as error:
        raise HTTPException(422, "Não foi possível converter a imagem para WebP.") from error

    media = Media(
        article_id=article_id,
        original_name=Path(image.filename or filename).name,
        file_path=str(path),
        url=f"/uploads/media/{filename}",
        mime_type="image/webp",
        alt_text=alt_text,
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    return media


async def save_newspaper_cover(image: UploadFile) -> str:
    """Valida e converte a capa do jornal para WebP, sem criar um registo Media."""
    content = await image.read()
    if not content:
        raise HTTPException(422, "A capa está vazia.")
    if len(content) > settings().max_upload_bytes:
        raise HTTPException(413, "A capa excede o limite de tamanho.")

    from io import BytesIO

    try:
        with Image.open(BytesIO(content)) as source:
            image_format = source.format
            if image_format not in ALLOWED_FORMATS:
                raise HTTPException(415, "A capa deve ser JPEG, PNG ou WebP.")
            if getattr(source, "n_frames", 1) > 1:
                raise HTTPException(422, "Capas animadas não são permitidas.")
            source.verify()
        with Image.open(BytesIO(content)) as source:
            converted = source.convert("RGBA" if source.mode in {"RGBA", "LA", "P"} else "RGB")
            directory = settings().upload_dir / "newspaper-covers"
            directory.mkdir(parents=True, exist_ok=True)
            filename = f"{uuid4().hex}.webp"
            converted.save(
                directory / filename,
                format="WEBP",
                quality=settings().image_webp_quality,
                method=6,
            )
    except (UnidentifiedImageError, OSError) as error:
        raise HTTPException(415, "A capa enviada não é uma imagem válida.") from error

    return f"/uploads/newspaper-covers/{filename}"
