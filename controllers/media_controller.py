from io import BytesIO
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

AUDIO_SIGNATURES = {
    b"ID3": ("audio/mpeg", ".mp3"),
    b"OggS": ("audio/ogg", ".ogg"),
    b"RIFF": ("audio/wav", ".wav"),
    b"fLaC": ("audio/flac", ".flac"),
}


def detect_audio(content: bytes) -> tuple[str, str] | None:
    for signature, result in AUDIO_SIGNATURES.items():
        if content.startswith(signature):
            return result
    # MPEG frame sync, usado por MP3 sem metadados ID3.
    if len(content) > 2 and content[0] == 0xFF and content[1] & 0xE0 == 0xE0:
        return "audio/mpeg", ".mp3"
    # ISO Base Media File: M4A/AAC contém a caixa ftyp no byte 4.
    if len(content) > 12 and content[4:8] == b"ftyp":
        return "audio/mp4", ".m4a"
    return None


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


async def upload_audio(
    db: Session,
    audio: UploadFile,
    article_id: int | None,
) -> Media:
    content = await audio.read()
    if not content:
        raise HTTPException(422, "O áudio está vazio.")
    if len(content) > settings().max_upload_bytes:
        raise HTTPException(413, "O áudio excede o limite de tamanho.")
    detected = detect_audio(content)
    if not detected:
        raise HTTPException(415, "São permitidos apenas MP3, OGG, WAV, FLAC e M4A válidos.")

    mime_type, extension = detected
    directory = settings().upload_dir / "audio"
    directory.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}{extension}"
    path = directory / filename
    path.write_bytes(content)
    media = Media(
        article_id=article_id,
        original_name=Path(audio.filename or filename).name,
        file_path=str(path),
        url=f"/uploads/audio/{filename}",
        mime_type=mime_type,
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
