"""Structured JSON error responses for the REST API."""
from __future__ import annotations

import logging

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler

logger = logging.getLogger("apps")


class ConflictError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "A conflicting resource already exists."
    default_code = "conflict"


class EligibilityError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Student is not eligible for this job."
    default_code = "not_eligible"

    def __init__(self, reasons: list[str] | None = None, detail=None, code=None):
        self.reasons = reasons or []
        payload = {"eligible": False, "reasons": self.reasons}
        super().__init__(detail=detail or payload, code=code)


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        logger.exception("Unhandled API exception", exc_info=exc)
        return None

    detail = response.data
    message = "Request failed."
    errors = detail
    if isinstance(detail, dict):
        if "detail" in detail and len(detail) == 1:
            message = str(detail["detail"])
            errors = {"detail": detail["detail"]}
        elif "eligible" in detail:
            message = "Eligibility check failed."
        else:
            message = "Validation failed."
    elif isinstance(detail, list) and detail:
        message = str(detail[0])

    response.data = {
        "success": False,
        "status": response.status_code,
        "message": message,
        "errors": errors,
    }
    return response
