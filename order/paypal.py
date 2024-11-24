# utils/paypal.py
import requests
from django.conf import settings

def get_paypal_access_token():
    url = f"{settings.PAYPAL_API_BASE_URL}/v1/oauth2/token"
    headers = {"Accept": "application/json", "Accept-Language": "en_US"}
    data = {"grant_type": "client_credentials"}
    auth = (settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET)

    response = requests.post(url, headers=headers, data=data, auth=auth)
    response.raise_for_status()
    return response.json().get("access_token")
