"""Interface para análise facial. Implementações ficam na camada de infraestrutura."""

from typing import Protocol
import numpy as np


class IFaceAnalyzer(Protocol):
    """Contrato para provedores de análise facial (InsightFace, etc.)."""

    def get_embedding(self, img: np.ndarray) -> np.ndarray:
        """
        Extrai o embedding da primeira face detectada na imagem.
        Raises:
            ValueError: Se nenhuma face for detectada ou embedding indisponível.
        """
        ...

    def has_face(self, img: np.ndarray) -> bool:
        """Verifica se há pelo menos um rosto na imagem."""
        ...
