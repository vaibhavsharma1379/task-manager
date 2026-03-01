"""
Custom exception handler that enforces a uniform API response envelope.

Every response — success or error — will share this shape:

  Success:
    {
      "success": true,
      "message": "...",
      "data": { ... }        # or a list for collections
    }

  Error:
    {
      "success": false,
      "message": "...",
      "errors": { "field": ["detail"] }   # optional, for validation errors
    }

Views use the `api_response` helper to build success responses.
DRF errors are caught here and re-shaped automatically.
"""

import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Call DRF's default handler first, then reformat the response.
    Unhandled exceptions (500s) bubble up as-is.
    """
    response = exception_handler(exc, context)

    if response is None:
        # Unhandled exception — log it and let Django handle the 500
        logger.exception("Unhandled exception in %s", context.get("view"))
        return None

    # Determine a human-friendly message
    message = _extract_message(response.data)

    # Build the uniform error envelope
    error_body = {
        "success": False,
        "message": message,
    }

    # Attach field-level validation errors if present
    if isinstance(response.data, dict) and _has_field_errors(response.data):
        error_body["errors"] = response.data

    response.data = error_body
    return response


def _extract_message(data) -> str:
    """Pull a readable string from whatever DRF put in response.data."""
    if isinstance(data, dict):
        # DRF wraps non-field errors under "detail" or "non_field_errors"
        if "detail" in data:
            return str(data["detail"])
        if "non_field_errors" in data:
            errors = data["non_field_errors"]
            return errors[0] if errors else "Validation error"
        return "Validation failed"
    if isinstance(data, list) and data:
        return str(data[0])
    return "An error occurred"


def _has_field_errors(data: dict) -> bool:
    """Return True if there are any field-level validation errors."""
    skip = {"detail", "non_field_errors"}
    return any(k not in skip for k in data)


def api_response(data=None, message="", status_code=status.HTTP_200_OK):
    """
    Helper used by views to build a uniform success response.

    Usage:
        return api_response(serializer.data, "Task created", status.HTTP_201_CREATED)
    """
    body = {
        "success": True,
        "message": message,
        "data": data,
    }
    return Response(body, status=status_code)
