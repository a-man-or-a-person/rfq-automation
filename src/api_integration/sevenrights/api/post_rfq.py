import time
import requests
from pydantic import ValidationError
from tenacity import RetryError
import json

from api_integration.config import get_settings
from api_integration.sevenrights.api.schemas.api_requests import RfqCreateRequest
from api_integration.sevenrights.api.schemas.api_results import RfqApiResult
from api_integration.sevenrights.api.utils import (
    _print_validation_errors,
    retry_network,
)


def post_rfq(data: dict, timeout: int = 30) -> RfqApiResult:
    """
    Create an RFQ via 7rights API.

    Network-transient failures are retried: transient connection/DNS errors
    (for example ``ConnectionError`` or ``NameResolutionError``) trigger up to 3
    attempts with exponential backoff (~2s, ~4s). HTTP responses, successful or
    not, are never retried. If retries are exhausted, the returned dict contains
    an ``error`` describing the last failure.

    Args:
        data: RFQ payload.
        timeout: Request timeout in seconds.

    Returns:
        Dict with ``error`` and ``rfq_id`` keys.
    """
    settings = get_settings()

    payload_data = data

    try:
        model = RfqCreateRequest.model_validate(payload_data)
    except ValidationError as exc:
        _print_validation_errors(exc)
        return {
            "error": f"ValidationError: {exc.errors()}",
            "rfq_id": None,
        }

    body = model.model_dump(mode="json", exclude_none=True)

    url = f"{settings.SEVEN_RIGHTS_API_URL.rstrip('/')}/rfq"

    headers = {
        "Authorization": f"Bearer {settings.SEVEN_RIGHTS_API_KEY}",
        "Content-Type": "application/json",
    }

    @retry_network(max_wait=settings.SEVEN_RIGHTS_API_AWAIT_TIMEOUT)
    def _post():
        return requests.post(url, headers=headers, json=body, timeout=timeout)

    try:
        response = _post()
    except RetryError as exc:
        last_exc = exc.last_attempt.exception()
        return {
            "error": f"Failed after 3 attempts: {type(last_exc).__name__}: {last_exc}",
            "rfq_id": None,
        }
    except requests.RequestException as exc:
        return {
            "error": str(exc),
            "rfq_id": None,
        }

    if response.status_code == 201:
        try:
            response_data = response.json()
        except ValueError:
            return {
                "error": "Invalid JSON in success response",
                "rfq_id": None,
            }

        rfq_id = response_data.get("id")
        if rfq_id is None:
            return {
                "error": "Missing 'id' in success response",
                "rfq_id": None,
            }

        return {
            "error": None,
            "rfq_id": rfq_id,
        }

    if response.status_code == 422:
        try:
            error_data = response.json()
        except ValueError:
            error_data = {}

        message = error_data.get("message", "Unknown validation error")
        errors = error_data.get("errors", {})

        return {
            "error": f"HTTP {response.status_code} ValidationError: {message} {errors}",
            "rfq_id": None,
        }

    return {
        "error": f"HTTP {response.status_code}: {response.text}",
        "rfq_id": None,
    }



