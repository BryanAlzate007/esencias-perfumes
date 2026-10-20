import requests
from django.conf import settings


def verify_recaptcha(token, remote_ip=""):
    secret = settings.RECAPTCHA_SECRET_KEY
    if not secret or not token:
        return False
    try:
        response = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={"secret": secret, "response": token, "remoteip": remote_ip},
            timeout=5,
        )
        payload = response.json()
    except (requests.RequestException, ValueError):
        return False
    return bool(payload.get("success"))
