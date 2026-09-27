from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError


ALLOWED_RESUME_EXTENSIONS = {".pdf", ".docx"}
ALLOWED_RESUME_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "application/octet-stream",
}
PDF_MAGIC = b"%PDF"
DOCX_MAGIC = b"PK"


def validate_resume_file(file) -> None:
    max_bytes = getattr(settings, "MAX_RESUME_SIZE_MB", 5) * 1024 * 1024
    size = getattr(file, "size", 0) or 0
    if size > max_bytes:
        raise ValidationError(f"Resume must be {settings.MAX_RESUME_SIZE_MB} MB or smaller.")

    name = getattr(file, "name", "") or ""
    ext = ""
    if "." in name:
        ext = "." + name.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_RESUME_EXTENSIONS:
        raise ValidationError("Resume must be a PDF or DOCX file.")

    content_type = (getattr(file, "content_type", None) or "").lower()
    if content_type and content_type not in ALLOWED_RESUME_CONTENT_TYPES:
        raise ValidationError("Resume file type is not allowed.")

    header = file.read(8)
    if hasattr(file, "seek"):
        file.seek(0)
    if ext == ".pdf" and not header.startswith(PDF_MAGIC):
        raise ValidationError("File content is not a valid PDF.")
    if ext == ".docx" and not header.startswith(DOCX_MAGIC):
        raise ValidationError("File content is not a valid DOCX archive.")
