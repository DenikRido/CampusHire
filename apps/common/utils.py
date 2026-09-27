from __future__ import annotations

import uuid
from pathlib import Path


def resume_upload_to(instance, filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in {".pdf", ".docx"}:
        ext = ".pdf"
    return f"resumes/{instance.user_id}/{uuid.uuid4().hex}{ext}"


def application_resume_upload_to(instance, filename: str) -> str:
    ext = Path(filename).suffix.lower() or ".pdf"
    return f"applications/{instance.student_id}/{uuid.uuid4().hex}{ext}"
