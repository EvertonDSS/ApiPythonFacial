"""
API de Verificação Facial - Entry point.
Utiliza InsightFace para comparar imagens e verificar faces.
"""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from api.v1.router import v1_router
from api.options.app_options import AppOptions

options = AppOptions()

app = FastAPI(
    title=options.title,
    description="""
## Visão Geral

Esta API utiliza **InsightFace** para verificar se duas imagens contêm a face da mesma pessoa.

### Funcionamento

1. Recebe duas imagens via upload (multipart/form-data)
2. Detecta rostos em cada imagem
3. Extrai embeddings (vetores de características) das faces
4. Calcula a similaridade de cosseno entre os embeddings
5. Retorna se são a mesma pessoa com base em um threshold configurável

### Requisitos das Imagens

- Formatos suportados: **JPEG, PNG**
- Deve conter **exatamente um rosto** visível em cada imagem
- Rostos parcialmente ocultos ou ângulos extremos podem reduzir a precisão

### Threshold de Similaridade

- **≥ 0.5**: Considerado a mesma pessoa
- **< 0.5**: Considerado pessoas diferentes
""",
    version=options.version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# API versionada: /api/v1/verify-faces, /api/v1/detect-face, /api/v1/health
app.include_router(v1_router, prefix="/api")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn

    from config.settings import HOST, PORT

    uvicorn.run(app, host=HOST, port=PORT)
