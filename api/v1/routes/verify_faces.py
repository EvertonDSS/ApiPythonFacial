"""Rota de verificação facial."""

from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Depends

from api.dependencies import get_face_analyzer
from api.v1.schemas.faces import VerificationResponse, ErrorResponse
from domain.interfaces.face_analyzer import IFaceAnalyzer
from domain.services.face_verification import verify_faces as verify_faces_service
from domain.validacao.image_validator import validate_image_content_type
from infrastructure.face_analysis.insightface_provider import image_to_numpy

router = APIRouter(prefix="/verify-faces", tags=["Faces"])


@router.post(
    "",
    response_model=VerificationResponse,
    responses={
        200: {"description": "Verificação realizada com sucesso", "model": VerificationResponse},
        400: {"description": "Imagem inválida ou nenhuma face detectada", "model": ErrorResponse},
        422: {"description": "Parâmetros inválidos", "model": ErrorResponse},
    },
    summary="Verificar se duas imagens são da mesma pessoa",
    description="""
Recebe duas imagens e retorna se contêm a face da mesma pessoa.

- **image1**: Primeira imagem contendo um rosto
- **image2**: Segunda imagem contendo um rosto
- **threshold** (opcional): Limiar de similaridade (padrão: 0.5). Valores entre 0 e 1.
""",
)
async def verify_faces(
    image1: UploadFile = File(
        ...,
        description="Primeira imagem (JPEG ou PNG) contendo um rosto",
    ),
    image2: UploadFile = File(
        ...,
        description="Segunda imagem (JPEG ou PNG) contendo um rosto",
    ),
    threshold: float = Form(
        0.5,
        description="Threshold de similaridade (0-1). Acima deste valor = mesma pessoa",
        ge=0.0,
        le=1.0,
    ),
    face_analyzer: IFaceAnalyzer = Depends(get_face_analyzer),
) -> VerificationResponse:
    """
    Compara duas imagens e verifica se contêm a face da mesma pessoa.
    Utiliza embeddings do InsightFace (ArcFace) e similaridade de cosseno.
    """
    for name, f in [("image1", image1), ("image2", image2)]:
        try:
            validate_image_content_type(getattr(f, "content_type", ""), name)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    try:
        content1 = await image1.read()
        content2 = await image2.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler arquivos: {str(e)}")

    try:
        img1 = image_to_numpy(content1)
        img2 = image_to_numpy(content2)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        emb1 = face_analyzer.get_embedding(img1)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Imagem 1: {str(e)}")

    try:
        emb2 = face_analyzer.get_embedding(img2)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Imagem 2: {str(e)}")

    same_person, similarity, msg = verify_faces_service(emb1, emb2, threshold)

    return VerificationResponse(
        same_person=same_person,
        similarity_score=round(similarity, 4),
        message=msg,
        embedding1=emb1.tolist(),
        embedding2=emb2.tolist(),
    )
