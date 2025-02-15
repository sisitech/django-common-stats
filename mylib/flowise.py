import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth

API_URL = settings.FLOWISE_API_URL # "https://flowise.cntb.onekana.ke/api/v1/prediction/b904409a-b3f1-4b71-b24a-1ad850cf28a0"
FLOWISE_USERNAME = settings.FLOWISE_USERNAME
FLOWISE_PASSWORD = settings.FLOWISE_PASSWORD

def flowiseAIQuery(business_name):
    payload={
    "question": business_name,
    }
    response = requests.post(API_URL, json=payload,auth=HTTPBasicAuth(FLOWISE_USERNAME, FLOWISE_PASSWORD))
    # print(response.status_code)
    # print(response.text)
    return response.json().get("json")