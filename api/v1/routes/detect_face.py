"""Rota de detecção de rosto."""

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends

from api.dependencies import get_face_analyzer
from api.v1.schemas.faces import FaceDetectionResponse, ErrorResponse
from domain.interfaces.face_analyzer import IFaceAnalyzer
from domain.validacao.image_validator import validate_image_content_type
from infrastructure.face_analysis.insightface_provider import image_to_numpy

router = APIRouter(prefix="/detect-face", tags=["Faces"])


@router.post(
    "",
    response_model=FaceDetectionResponse,
    responses={
        200: {"description": "Detecção realizada com sucesso", "model": FaceDetectionResponse},
        400: {"description": "Imagem inválida", "model": ErrorResponse},
        422: {"description": "Parâmetros inválidos", "model": ErrorResponse},
    },
    summary="Verificar se uma imagem contém um rosto",
    description="""
Recebe uma única imagem e informa se há pelo menos um rosto detectado na foto.

- **image**: Imagem JPEG ou PNG contendo (ou não) um rosto.
""",
)
async def detect_face(
    image: UploadFile = File(
        ...,
        description="Imagem (JPEG ou PNG) que será analisada para detecção de rosto",
    ),
    face_analyzer: IFaceAnalyzer = Depends(get_face_analyzer),
) -> FaceDetectionResponse:
    """
    Verifica se uma imagem contém pelo menos um rosto detectado pelo InsightFace.
    Não realiza comparação, apenas detecção.
    """
    try:
        validate_image_content_type(image.content_type, "image")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        content = await image.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler arquivo: {str(e)}")

    try:
        img = image_to_numpy(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    has_face = face_analyzer.has_face(img)

    if has_face:
        msg = "Foi detectado pelo menos um rosto na imagem."
    else:
        msg = "Nenhum rosto foi detectado na imagem."

    return FaceDetectionResponse(has_face=has_face, message=msg)
