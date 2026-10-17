import hashlib
import hmac
import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.conf import settings

TRANSACTION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9\-]{0,63}$")
_MISSING = object()


class WompiRequestError(Exception):
    def __init__(self, status_code=None):
        self.status_code = status_code
        super().__init__("Wompi request failed")


def integrity_signature(reference, amount_in_cents, currency, secret, expiration_time=""):
    # Wompi hashes reference + amount + currency + optional expiration + integrity secret.
    payload = f"{reference}{amount_in_cents}{currency}"
    if expiration_time:
        payload += expiration_time
    payload += secret
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def signatures_match(expected, received):
    if not isinstance(expected, str) or not isinstance(received, str):
        return False
    left = expected.strip().lower()
    right = received.strip().lower()
    if len(left) != len(right):
        return False
    return hmac.compare_digest(left, right)


def _dig(data, path):
    current = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return _MISSING
        current = current[part]
    return current


def _canonical(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if value is None:
        return ""
    return str(value)


def event_checksum(data, properties, timestamp, secret):
    parts = []
    for prop in properties:
        value = _dig(data, prop)
        if value is _MISSING:
            return None
        parts.append(_canonical(value))
    payload = "".join(parts) + str(timestamp) + secret
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def expected_environment():
    key = settings.WOMPI_PUBLIC_KEY or ""
    if key.startswith("pub_prod_"):
        return "prod"
    return "test"


def verify_event(payload, header_checksum):
    signature = payload.get("signature") if isinstance(payload, dict) else None
    if not isinstance(signature, dict):
        return False
    properties = signature.get("properties")
    checksum = signature.get("checksum")
    timestamp = signature.get("timestamp")
    data = payload.get("data")
    if not isinstance(properties, list) or not properties or not isinstance(checksum, str):
        return False
    if timestamp is None or not isinstance(data, dict):
        return False
    if any(not isinstance(prop, str) for prop in properties):
        return False
    if header_checksum and not signatures_match(checksum, header_checksum):
        return False
    if payload.get("environment") != expected_environment():
        return False
    secret = settings.WOMPI_EVENTS_SECRET or ""
    if not secret:
        return False
    expected = event_checksum(data, properties, timestamp, secret)
    if expected is None:
        return False
    return signatures_match(expected, checksum)


def fetch_transaction(transaction_id):
    if not isinstance(transaction_id, str) or not TRANSACTION_ID.fullmatch(transaction_id):
        raise WompiRequestError(status_code=400)
    private_key = settings.WOMPI_PRIVATE_KEY or ""
    if not private_key:
        raise WompiRequestError()
    url = f"{settings.WOMPI_API_URL.rstrip('/')}/transactions/{quote(transaction_id, safe='')}"
    request = Request(url, headers={"Authorization": f"Bearer {private_key}", "Accept": "application/json"})
    try:
        with urlopen(request, timeout=10) as response:
            body = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raise WompiRequestError(status_code=error.code) from error
    except (URLError, TimeoutError, json.JSONDecodeError, UnicodeError) as error:
        raise WompiRequestError() from error
    transaction = body.get("data") if isinstance(body, dict) else None
    if not isinstance(transaction, dict):
        raise WompiRequestError()
    return transaction
