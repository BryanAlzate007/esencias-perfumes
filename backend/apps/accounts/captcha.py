import requests
from django.conf import settings


def verify_recaptcha(token, remote_ip=""):
    api_key = settings.RECAPTCHA_API_KEY
    site_key = settings.RECAPTCHA_SITE_KEY
    project_id = settings.RECAPTCHA_PROJECT_ID
    if not api_key or not site_key or not project_id or not token:
        return False
    event = {
        "token": token,
        "siteKey": site_key,
        "expectedAction": settings.RECAPTCHA_ACTION,
    }
    if remote_ip:
        event["userIpAddress"] = remote_ip
    url = (
        "https://recaptchaenterprise.googleapis.com/v1/projects/"
        f"{project_id}/assessments?key={api_key}"
    )
    try:
        response = requests.post(url, json={"event": event}, timeout=5)
        payload = response.json()
    except (requests.RequestException, ValueError):
        return False
    properties = payload.get("tokenProperties") or {}
    return bool(properties.get("valid")) and properties.get("action") == settings.RECAPTCHA_ACTION
