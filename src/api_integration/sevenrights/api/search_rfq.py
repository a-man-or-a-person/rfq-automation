import time
import requests
from pathlib import Path

from api_integration.config import get_settings
from api_integration.sevenrights.api.schemas.api_results import RfqApiResult


def search_rfq(title: str, timeout: int = 30) -> RfqApiResult:
    """Searches for existing RFQs by title (API restriction).
    TODO: Very rude. Needs improvement
    """
    settings = get_settings()

    url = f"{settings.SEVEN_RIGHTS_API_URL.rstrip('/')}/rfq"

    headers = {
        "Authorization": f"Bearer {settings.SEVEN_RIGHTS_API_KEY}",
        "Accept": "application/json",
    }

    params = {"search": title, "page": 1, "perPage": 50}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=timeout)
    except requests.RequestException as exc:
        return {
            "error": str(exc),
            "rfq_id": None,
        }

    if response.status_code == 401:
        try:
            error_data = response.json()
        except ValueError:
            error_data = {}

        message = error_data.get("message", "Unauthorized")
        return {
            "error": f"HTTP {response.status_code}: {message}",
            "rfq_id": None,
        }

    if response.status_code != 200:
        return {
            "error": f"HTTP {response.status_code}: {response.text}",
            "rfq_id": None,
        }

    try:
        data = response.json()
    except ValueError:
        return {
            "error": "Invalid JSON in success response",
            "rfq_id": None,
        }

    items = data.get("data") or []
    if not items:
        return {
            "error": None,
            "rfq_id": None,
        }

    rfq_id = items[0].get("id")
    return {
        "error": None,
        "rfq_id": rfq_id,
    }



