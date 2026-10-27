from io import BytesIO

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException

from config import settings


def _client():
    cfg = settings()
    if not all([cfg.r2_endpoint_url, cfg.r2_bucket_name, cfg.r2_access_key_id, cfg.r2_secret_access_key]):
        raise HTTPException(503, "Armazenamento R2 não está configurado.")
    return boto3.client(
        "s3",
        endpoint_url=cfg.r2_endpoint_url,
        aws_access_key_id=cfg.r2_access_key_id,
        aws_secret_access_key=cfg.r2_secret_access_key,
        region_name="auto",
    )


def upload_bytes(key: str, content: bytes, content_type: str, public: bool) -> str:
    cfg = settings()
    try:
        _client().put_object(
            Bucket=cfg.r2_bucket_name,
            Key=key,
            Body=content,
            ContentType=content_type,
            CacheControl="public, max-age=31536000, immutable" if public else "private, no-store",
        )
    except (BotoCoreError, ClientError) as error:
        raise HTTPException(502, "Não foi possível enviar o ficheiro para o R2.") from error
    if public:
        if not cfg.r2_public_base_url:
            raise HTTPException(503, "R2_PUBLIC_BASE_URL não está configurado.")
        return f"{cfg.r2_public_base_url.rstrip('/')}/{key}"
    return key


def create_private_pdf_upload() -> tuple[str, str]:
    """Cria uma URL temporária; credenciais R2 nunca são enviadas ao browser."""
    cfg = settings()
    from uuid import uuid4
    key = f"newspapers/{uuid4().hex}.pdf"
    try:
        url = _client().generate_presigned_url(
            "put_object",
            Params={"Bucket": cfg.r2_bucket_name, "Key": key, "ContentType": "application/pdf"},
            ExpiresIn=900,
            HttpMethod="PUT",
        )
    except (BotoCoreError, ClientError) as error:
        raise HTTPException(502, "Não foi possível preparar o envio directo ao R2.") from error
    return key, url


def private_pdf_size(key: str) -> int:
    if not key.startswith("newspapers/") or not key.endswith(".pdf"):
        raise HTTPException(422, "Referência de PDF inválida.")
    try:
        result = _client().head_object(Bucket=settings().r2_bucket_name, Key=key)
        if result.get("ContentType") != "application/pdf":
            raise HTTPException(415, "O ficheiro enviado não é um PDF.")
        return int(result.get("ContentLength", 0))
    except HTTPException:
        raise
    except (BotoCoreError, ClientError) as error:
        raise HTTPException(422, "O PDF não foi encontrado no R2.") from error


def download_private(key: str):
    try:
        return _client().get_object(Bucket=settings().r2_bucket_name, Key=key)
    except (BotoCoreError, ClientError) as error:
        raise HTTPException(410, "O ficheiro já não está disponível.") from error
