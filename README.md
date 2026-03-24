# API de Verificação Facial

API REST que recebe duas imagens e verifica se são da mesma pessoa utilizando **InsightFace** para detecção e reconhecimento facial. Documentação interativa via **Swagger/OpenAPI**.

## Funcionalidades

- Recebe duas imagens (JPEG/PNG) via upload
- Detecta rostos com InsightFace (SCRFD)
- Extrai embeddings faciais (ArcFace)
- Calcula similaridade de cosseno
- Retorna se são a mesma pessoa + score de similaridade
- Documentação Swagger em `/docs` e ReDoc em `/redoc`

## Instalação

```bash
# Criar ambiente virtual (recomendado)
python -m venv venv
venv\Scripts\activate   # Windows
# ou: source venv/bin/activate   # Linux/Mac

# Instalar dependências
pip install -r requirements.txt
```

### Windows – Erro de compilação

Se aparecer erro de **Microsoft Visual C++ 14.0 required**, você pode:

1. **Instalar o Visual C++ Build Tools**  
   https://visualstudio.microsoft.com/visual-cpp-build-tools/

2. **Ou usar wheels pré-compilados**  
   https://github.com/cobanov/insightface_windows  
   Baixe o wheel para sua versão do Python e instale:
   ```bash
   pip install insightface-0.7.3-cp311-cp311-win_amd64.whl  # ajuste cp311 se necessário
   pip install fastapi uvicorn python-multipart onnxruntime opencv-python-headless numpy
   ```

### macOS (MacBook M1/M2/M3/M4 – Apple Silicon)

O projeto roda normalmente. Para melhor desempenho, use o ONNX Runtime para Silicon (CoreML):

```bash
pip install -r requirements-mac.txt
```

O código já usa **CoreML** automaticamente quando disponível (via `onnxruntime-silicon`).

Na primeira execução, o InsightFace baixará automaticamente o modelo `buffalo_l` (~326MB).

## Execução

```bash
# Iniciar servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Ou:

```bash
python main.py
```

## Estrutura do Projeto (Clean Architecture)

```
facial2/
├── domain/           # Regras de negócio, interfaces, validações
├── infrastructure/   # InsightFace, implementações externas
├── api/              # Controllers, schemas (DTOs), options
│   └── v1/           # API versionada
├── config/           # Configurações (appsettings)
└── main.py           # Entry point
```

## Uso

### Swagger UI

Acesse **http://localhost:8000/docs** para documentação interativa.

1. Clique em **POST /api/v1/verify-faces**
2. Clique em **Try it out**
3. Faça upload de duas imagens (image1 e image2)
4. Opcionalmente altere o threshold (padrão: 0.5)
5. Clique em **Execute**

### cURL

```bash
curl -X POST "http://localhost:8000/api/v1/verify-faces" ^
  -F "image1=@foto1.jpg" ^
  -F "image2=@foto2.jpg" ^
  -F "threshold=0.5"
```

### Python (requests)

```python
import requests

url = "http://localhost:8000/api/v1/verify-faces"
files = {
    "image1": open("foto1.jpg", "rb"),
    "image2": open("foto2.jpg", "rb"),
}
data = {"threshold": 0.5}

r = requests.post(url, files=files, data=data)
print(r.json())
# {"same_person": true, "similarity_score": 0.78, "message": "...", "embedding1": [...], "embedding2": [...]}
```

## Resposta da API

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `same_person` | bool | Se as imagens são da mesma pessoa |
| `similarity_score` | float | Similaridade de cosseno (-1 a 1) |
| `message` | str | Mensagem descritiva |
| `embedding1` | list[float] | Vetor da face na imagem 1 |
| `embedding2` | list[float] | Vetor da face na imagem 2 |

## Threshold

- **≥ 0.5** (padrão): mesma pessoa
- **< 0.5**: pessoas diferentes

Para maior precisão em cenários críticos, use threshold maior (ex: 0.6). Para mais recall, use menor (ex: 0.4).

## Requisitos das imagens

- Formatos: JPEG, PNG
- Uma face visível por imagem
- Qualidade adequada para detecção

## Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/verify-faces` | Verifica se duas imagens são da mesma pessoa |
| POST | `/api/v1/detect-face` | Verifica se uma imagem contém rosto |
| GET | `/api/v1/health` | Health check |
