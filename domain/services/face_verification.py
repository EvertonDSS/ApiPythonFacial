"""Serviço de verificação facial - similaridade e decisão."""

import numpy as np


def cosine_similarity(emb1: np.ndarray, emb2: np.ndarray) -> float:
    """Calcula similaridade de cosseno entre dois embeddings."""
    return float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))


def verify_faces(
    emb1: np.ndarray,
    emb2: np.ndarray,
    threshold: float = 0.5,
) -> tuple[bool, float, str]:
    """
    Compara dois embeddings e retorna se são da mesma pessoa.

    Returns:
        Tuple (same_person, similarity_score, message).
    """
    similarity = cosine_similarity(emb1, emb2)
    same_person = similarity >= threshold

    if same_person:
        msg = (
            f"As faces apresentam alta similaridade ({similarity:.2f}) - "
            "provavelmente a mesma pessoa."
        )
    else:
        msg = (
            f"As faces apresentam baixa similaridade ({similarity:.2f}) - "
            "pessoas diferentes."
        )

    return same_person, similarity, msg
