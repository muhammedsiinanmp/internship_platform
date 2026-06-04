from rest_framework.response import Response
from rest_framework import status


class SuccessResponseMixin:
    """Mixin that wraps successful responses in a consistent envelope."""

    def success_response(self, data=None, message="", http_status=status.HTTP_200_OK):
        payload = {"status": "success", "message": message}
        if data is not None:
            payload["data"] = data
        return Response(payload, status=http_status)
