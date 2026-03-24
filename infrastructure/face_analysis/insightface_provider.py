"""Implementação do FaceAnalyzer usando InsightFace."""

import numpy as np


def _get_onnx_providers() -> list[str]:
    """Escolhe providers do ONNX: CoreML no Mac M1/M2/M3/M4, CPU no resto."""
    try:
        import onnxruntime

        available = onnxruntime.get_available_providers()
        if "CoreMLExecutionProvider" in available:
            return ["CoreMLExecutionProvider", "CPUExecutionProvider"]
    except Exception:
        pass
    return ["CPUExecutionProvider"]


def image_to_numpy(content: bytes) -> np.ndarray:
    """Converte bytes da imagem em array numpy (BGR) para OpenCV."""
    import cv2

    nparr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Imagem inválida ou formato não suportado")
    return img


class InsightFaceProvider:
    """Provedor de análise facial usando InsightFace (buffalo_l)."""

    _instance = None

    def __new__(cls) -> "InsightFaceProvider":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_app") and self._app is not None:
            return
        from insightface.app import FaceAnalysis

        providers = _get_onnx_providers()
        self._app = FaceAnalysis(name="buffalo_l", providers=providers)
        self._app.prepare(ctx_id=0, det_size=(640, 640))

    def get_embedding(self, img: np.ndarray) -> np.ndarray:
        """Extrai o embedding da primeira face detectada na imagem."""
        faces = self._app.get(img)
        if not faces:
            raise ValueError("Nenhuma face detectada na imagem")
        if not hasattr(faces[0], "embedding") or faces[0].embedding is None:
            raise ValueError("Não foi possível extrair embedding facial")
        return faces[0].embedding

    def has_face(self, img: np.ndarray) -> bool:
        """Verifica se há pelo menos um rosto na imagem."""
        faces = self._app.get(img)
        return bool(faces)
