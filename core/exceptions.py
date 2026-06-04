import logging
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns a consistent JSON error envelope.
    """
    # Let DRF handle the initial conversion
    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(detail=exc.message_dict)

    if isinstance(exc, Http404):
        exc = exceptions.NotFound()

    response = exception_handler(exc, context)

    if response is not None:
        error_payload = {
            "status": "error",
            "code": response.status_code,
            "errors": response.data,
        }
        response.data = error_payload
        return response

    # Unhandled exception — log it and return 500
    logger.exception("Unhandled exception", exc_info=exc)
    return Response(
        {
            "status": "error",
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "errors": {"detail": "An unexpected error occurred. Please try again later."},
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
