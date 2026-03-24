"""Configurações carregadas de ambiente (equivalente a appsettings)."""

import os

# Pode ser expandido para usar python-dotenv ou pydantic-settings
# por ora valores padrão
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
