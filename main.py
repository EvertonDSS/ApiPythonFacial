"""
API de Verificação Facial - InsightFace para comparar e detectar faces.
"""

from fastapi import FastAPI, File, Form, UploadFile, HTTPException

from face_service import (
    image_to_numpy,
    get_embedding,
    has_face,
    cosine_similarity,
    ALLOWED_TYPES,
)
from schemas import FaceDetectionResponse, VerificationResponse, ErrorResponse

app = FastAPI(
    title="API de Verificação Facial",
    description="""
API que utiliza **InsightFace** para verificar se duas imagens são da mesma pessoa
e para detectar se uma imagem contém rosto.

- **POST /api/v1/verify-faces**: Compara duas imagens
- **POST /api/v1/detect-face**: Verifica se imagem tem rosto
- **GET /api/v1/health**: Health check
""",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


def _validate_image(f: UploadFile, name: str) -> None:
    ct = (getattr(f, "content_type", "") or "").lower()
    if ct not in ALLOWED_TYPES:
        raise HTTPException(400, f"{name}: formato não suportado. Use JPEG ou PNG.")


@app.post(
    "/api/v1/verify-faces",
    response_model=VerificationResponse,
    responses={400: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
    summary="Verificar se duas imagens são da mesma pessoa",
)
async def verify_faces(
    image1: UploadFile = File(..., description="Primeira imagem"),
    image2: UploadFile = File(..., description="Segunda imagem"),
    threshold: float = Form(0.5, ge=0.0, le=1.0, description="Limiar de similaridade"),
):
    """Compara duas imagens e retorna se são da mesma pessoa + embeddings."""
    for name, f in [("image1", image1), ("image2", image2)]:
        _validate_image(f, name)

    try:
        img1 = image_to_numpy(await image1.read())
        img2 = image_to_numpy(await image2.read())
    except ValueError as e:
        raise HTTPException(400, str(e))

    try:
        emb1 = get_embedding(img1)
    except ValueError as e:
        raise HTTPException(400, f"Imagem 1: {e}")

    try:
        emb2 = get_embedding(img2)
    except ValueError as e:
        raise HTTPException(400, f"Imagem 2: {e}")

    sim = cosine_similarity(emb1, emb2)
    same = sim >= threshold
    msg = (
        f"As faces apresentam {'alta' if same else 'baixa'} similaridade ({sim:.2f}) - "
        f"{'provavelmente a mesma pessoa' if same else 'pessoas diferentes'}."
    )

    return VerificationResponse(
        same_person=same,
        similarity_score=round(sim, 4),
        message=msg,
        embedding1=emb1.tolist(),
        embedding2=emb2.tolist(),
    )


@app.post(
    "/api/v1/detect-face",
    response_model=FaceDetectionResponse,
    responses={400: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
    summary="Verificar se imagem contém rosto",
)
async def detect_face(image: UploadFile = File(..., description="Imagem para análise")):
    """Retorna se a imagem contém pelo menos um rosto."""
    _validate_image(image, "image")

    try:
        img = image_to_numpy(await image.read())
    except ValueError as e:
        raise HTTPException(400, str(e))

    has = has_face(img)
    return FaceDetectionResponse(
        has_face=has,
        message="Foi detectado pelo menos um rosto." if has else "Nenhum rosto detectado.",
    )


@app.get("/api/v1/health", tags=["Sistema"])
async def health():
    """Health check."""
    return {"status": "ok", "service": "facial-verification-api"}


if __name__ == "__main__":
    import uvicorn
    import os
    uvicorn.run(app, host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", "8000")))
