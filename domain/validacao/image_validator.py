"""Validação de imagens para processamento facial."""

ALLOWED_CONTENT_TYPES = ("image/jpeg", "image/jpg", "image/png")


def validate_image_content_type(content_type: str | None, field_name: str = "imagem") -> None:
    """
    Valida o content-type da imagem.
    Raises:
        ValueError: Se o formato não for suportado.
    """
    ct = (content_type or "").lower()
    if ct not in ALLOWED_CONTENT_TYPES:
        raise ValueError(f"{field_name}: formato não suportado. Use JPEG ou PNG.")
