"""Schemas (DTOs) da API."""

from pydantic import BaseModel


class FaceDetectionResponse(BaseModel):
    has_face: bool
    message: str


class VerificationResponse(BaseModel):
    same_person: bool
    similarity_score: float
    message: str
    embedding1: list[float]
    embedding2: list[float]


class ErrorResponse(BaseModel):
    detail: str
