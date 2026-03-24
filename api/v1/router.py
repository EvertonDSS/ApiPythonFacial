"""Router agregado da API v1."""

from fastapi import APIRouter

from api.v1.routes import verify_faces, detect_face, health

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(verify_faces.router)
v1_router.include_router(detect_face.router)
v1_router.include_router(health.router)
