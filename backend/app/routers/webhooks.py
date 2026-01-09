"""
Webhooks Router - Endpoints para notificaciones de eventos
"""
from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
import httpx
import hashlib
import hmac
import json

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

# In-memory webhook registry (en producción usar DB)
webhook_registry: Dict[str, Dict[str, Any]] = {}


class WebhookConfig(BaseModel):
    url: HttpUrl
    events: List[str] = ["generation.complete", "generation.failed", "batch.complete"]
    secret: Optional[str] = None
    enabled: bool = True


class WebhookResponse(BaseModel):
    webhook_id: str
    url: str
    events: List[str]
    created_at: datetime


@router.post("/register", response_model=WebhookResponse)
async def register_webhook(config: WebhookConfig):
    """
    Registra un nuevo webhook para recibir notificaciones de eventos
    """
    webhook_id = hashlib.sha256(
        f"{config.url}{datetime.now().isoformat()}".encode()
    ).hexdigest()[:16]

    webhook_registry[webhook_id] = {
        "url": str(config.url),
        "events": config.events,
        "secret": config.secret,
        "enabled": config.enabled,
        "created_at": datetime.now(),
        "last_triggered": None,
        "failure_count": 0
    }

    return WebhookResponse(
        webhook_id=webhook_id,
        url=str(config.url),
        events=config.events,
        created_at=webhook_registry[webhook_id]["created_at"]
    )


@router.get("/list")
async def list_webhooks():
    """
    Lista todos los webhooks registrados
    """
    return {
        "webhooks": [
            {
                "webhook_id": wid,
                "url": data["url"],
                "events": data["events"],
                "enabled": data["enabled"],
                "created_at": data["created_at"].isoformat(),
                "last_triggered": data["last_triggered"].isoformat() if data["last_triggered"] else None,
                "failure_count": data["failure_count"]
            }
            for wid, data in webhook_registry.items()
        ]
    }


@router.delete("/{webhook_id}")
async def delete_webhook(webhook_id: str):
    """
    Elimina un webhook registrado
    """
    if webhook_id not in webhook_registry:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    del webhook_registry[webhook_id]
    return {"message": "Webhook deleted"}


async def trigger_webhook(event_type: str, payload: Dict[str, Any]):
    """
    Dispara un webhook para todos los registros que escuchan este evento
    """
    for webhook_id, webhook_data in webhook_registry.items():
        if not webhook_data["enabled"]:
            continue
        
        if event_type not in webhook_data["events"]:
            continue

        try:
            # Preparar payload
            webhook_payload = {
                "event": event_type,
                "timestamp": datetime.now().isoformat(),
                "data": payload
            }

            # Añadir firma si hay secret
            headers = {"Content-Type": "application/json"}
            if webhook_data["secret"]:
                signature = hmac.new(
                    webhook_data["secret"].encode(),
                    json.dumps(webhook_payload).encode(),
                    hashlib.sha256
                ).hexdigest()
                headers["X-Webhook-Signature"] = f"sha256={signature}"

            # Enviar webhook
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    webhook_data["url"],
                    json=webhook_payload,
                    headers=headers
                )
                response.raise_for_status()

            # Actualizar registro
            webhook_data["last_triggered"] = datetime.now()
            webhook_data["failure_count"] = 0

        except Exception as e:
            # Incrementar contador de fallos
            webhook_data["failure_count"] = webhook_data.get("failure_count", 0) + 1
            print(f"Webhook {webhook_id} failed: {e}")
            
            # Deshabilitar después de 5 fallos consecutivos
            if webhook_data["failure_count"] >= 5:
                webhook_data["enabled"] = False


# Exportar función para uso en otros routers
__all__ = ["router", "trigger_webhook"]
