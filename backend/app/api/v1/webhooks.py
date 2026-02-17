"""Webhook Endpoints"""
from fastapi import APIRouter, Request

router = APIRouter()


@router.post("/regulation-update")
async def regulation_update_webhook(request: Request):
    """Webhook for external regulation update notifications"""
    body = await request.json()
    return {"status": "received", "event": "regulation_update", "data": body}


@router.post("/payment")
async def payment_webhook(request: Request):
    """Webhook for payment gateway callbacks"""
    body = await request.json()
    return {"status": "received", "event": "payment", "data": body}
