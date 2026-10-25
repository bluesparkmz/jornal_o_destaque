from decimal import Decimal
from uuid import uuid4

import httpx
from fastapi import HTTPException

from config import settings


def _headers() -> dict[str, str]:
    cfg = settings()
    if not cfg.skywallet_sk_id or not cfg.skywallet_api_key:
        raise HTTPException(503, "Pagamentos M-Pesa ainda não estão configurados.")
    return {
        "X-SK-ID": cfg.skywallet_sk_id,
        "X-API-Key": cfg.skywallet_api_key,
        "Content-Type": "application/json",
    }


def create_payment(msisdn: str, amount_cents: int, description: str) -> str:
    """Pede o pagamento M-Pesa e devolve o order_id local a consultar."""
    cfg = settings()
    order_id = f"ODESTAQUE-{uuid4().hex[:20].upper()}"
    amount = str(Decimal(amount_cents) / Decimal(100))
    try:
        response = httpx.post(
            f"{cfg.skywallet_base_url.rstrip('/')}/api/developer/payment/request",
            headers=_headers(),
            json={
                "msisdn": msisdn,
                "amount": amount,
                "currency": "MZN",
                "description": description[:250],
                "order_id": order_id,
            },
            timeout=50,
        )
        response.raise_for_status()
    except httpx.HTTPError as error:
        raise HTTPException(502, "Não foi possível iniciar o pagamento M-Pesa.") from error
    return order_id


def payment_status(order_id: str) -> str:
    cfg = settings()
    try:
        response = httpx.get(
            f"{cfg.skywallet_base_url.rstrip('/')}/api/developer/payment/status",
            headers=_headers(),
            params={"order_id": order_id},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPError, ValueError) as error:
        raise HTTPException(502, "Não foi possível confirmar o estado do pagamento.") from error
    state = str(data.get("status", "pending")).lower()
    if state not in {"success", "failed", "pending"}:
        return "pending"
    return state
