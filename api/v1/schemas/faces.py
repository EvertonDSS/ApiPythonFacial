"""Schemas (DTOs) para endpoints de faces."""

from pydantic import BaseModel


class FaceDetectionResponse(BaseModel):
    """Resposta da detecção de rosto em uma imagem."""

    has_face: bool
    """Indica se foi detectado pelo menos um rosto na imagem."""

    message: str
    """Mensagem descritiva do resultado."""


class VerificationResponse(BaseModel):
    """Resposta da verificação facial."""

    same_person: bool
    """Indica se as duas imagens são da mesma pessoa."""

    similarity_score: float
    """Score de similaridade de cosseno (-1 a 1). Acima de ~0.5 indica mesma pessoa."""

    message: str
    """Mensagem descritiva do resultado."""

    embedding1: list[float]
    """Vetor de características da face na primeira imagem (ArcFace)."""

    embedding2: list[float]
    """Vetor de características da face na segunda imagem (ArcFace)."""

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "same_person": True,
                    "similarity_score": 0.78,
                    "message": "As faces apresentam alta similaridade - provavelmente a mesma pessoa.",
                    "embedding1": [0.1, -0.2],
                    "embedding2": [0.1, -0.2],
                },
                {
                    "same_person": False,
                    "similarity_score": 0.21,
                    "message": "As faces apresentam baixa similaridade - pessoas diferentes.",
                    "embedding1": [0.1, -0.2],
                    "embedding2": [-0.3, 0.5],
                },
            ]
        }


class ErrorResponse(BaseModel):
    """Resposta de erro."""

    detail: str
