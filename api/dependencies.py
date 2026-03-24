"""Injeção de dependências."""

from fastapi import Depends
from infrastructure.face_analysis.insightface_provider import InsightFaceProvider
from domain.interfaces.face_analyzer import IFaceAnalyzer


def get_face_analyzer() -> IFaceAnalyzer:
    """Retorna o provedor de análise facial (singleton)."""
    return InsightFaceProvider()
