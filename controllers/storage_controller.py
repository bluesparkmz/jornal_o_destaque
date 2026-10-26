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


def download_private(key: str):
    try:
        return _client().get_object(Bucket=settings().r2_bucket_name, Key=key)
    except (BotoCoreError, ClientError) as error:
        raise HTTPException(410, "O ficheiro já não está disponível.") from error
