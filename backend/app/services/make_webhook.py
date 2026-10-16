import json, os, urllib.error, urllib.request


def send_draft_event(payload: dict) -> str:
    url=os.getenv('MAKE_DRAFT_WEBHOOK_URL')
    if not url:
        return 'not_configured'
    request=urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type':'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            if 200 <= response.status < 300:
                return 'sent'
            return 'failed'
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
        return 'failed'
