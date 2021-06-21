
# This file is part of the carrier_send_shipments_shippypro module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from requests.auth import HTTPBasicAuth
import requests
import base64
import json

API_URL = 'https://www.shippypro.com/api'

def shippypro_send(api, values):
    if api.shippypro_api_key:
        return requests.post(API_URL,
            auth=HTTPBasicAuth(api.username, api.password),
            data=json.dumps(values),
            timeout=api.timeout)
    else:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic %s' % base64.b64encode(
                bytes('%s:%s' % (api.username, api.password), 'utf-8'))
        }
        return requests.post(API_URL,
            data=json.dumps(values),
            headers=headers,
            timeout=api.timeout)
