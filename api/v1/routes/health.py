"""Rota de health check."""

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Sistema"])


@router.get("")
async def health():
    """Health check da API."""
    return {"status": "ok", "service": "facial-verification-api"}
