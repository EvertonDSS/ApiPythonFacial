"""
Serviço de análise facial - InsightFace (detecção, embeddings, verificação).
"""

import numpy as np

# Singleton
_face_app = None
ALLOWED_TYPES = ("image/jpeg", "image/jpg", "image/png")


def _get_face_app():
    """Retorna o FaceAnalysis (singleton, lazy load)."""
    global _face_app
    if _face_app is None:
        try:
            import onnxruntime
            providers = ["CoreMLExecutionProvider", "CPUExecutionProvider"] \
                if "CoreMLExecutionProvider" in onnxruntime.get_available_providers() \
                else ["CPUExecutionProvider"]
        except Exception:
            providers = ["CPUExecutionProvider"]

        from insightface.app import FaceAnalysis
        _face_app = FaceAnalysis(name="buffalo_l", providers=providers)
        _face_app.prepare(ctx_id=0, det_size=(640, 640))
    return _face_app


def image_to_numpy(content: bytes) -> np.ndarray:
    """Converte bytes em array numpy (BGR) para OpenCV."""
    import cv2
    img = cv2.imdecode(np.frombuffer(content, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Imagem inválida ou formato não suportado")
    return img


def get_embedding(img: np.ndarray) -> np.ndarray:
    """Extrai embedding da primeira face detectada."""
    faces = _get_face_app().get(img)
    if not faces or not getattr(faces[0], "embedding", None):
        raise ValueError("Nenhuma face detectada na imagem")
    return faces[0].embedding


def has_face(img: np.ndarray) -> bool:
    """Verifica se há pelo menos um rosto na imagem."""
    return bool(_get_face_app().get(img))


def cosine_similarity(emb1: np.ndarray, emb2: np.ndarray) -> float:
    """Similaridade de cosseno entre dois embeddings."""
    return float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))
