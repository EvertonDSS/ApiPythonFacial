"""Configurações da aplicação (similar ao Options Pattern do .NET)."""


class FaceAnalysisOptions:
    """Opções do modelo de análise facial."""

    model_name: str = "buffalo_l"
    det_size: tuple[int, int] = (640, 640)
    default_threshold: float = 0.5


class AppOptions:
    """Opções gerais da aplicação."""

    title: str = "API de Verificação Facial"
    version: str = "1.0.0"
    face_analysis: FaceAnalysisOptions = FaceAnalysisOptions()
