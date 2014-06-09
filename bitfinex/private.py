# !/usr/bin/env python

import logging
import hmac
import json
import base64
import hashlib
import time

from exchangelib.utils import post

log = logging.getLogger(__name__)

__all__ = ['Auth', 'active_orders']

API_VERSION = 'v1'
PRIVATE_API_URL = "https://api.bitfinex.com/" + API_VERSION + '/'


# todo handle bitfinex errors
# with http status 400:
# {"message":"Must specify a 'request' field in the payload that matches the URL path."}


class Auth(object):
    exchange = 'bitstamp'

    def __init__(self, key, secret):
        self.secret = secret
        self.key = key
        self.nonce = 0

    def sign(self, data):
        """
        :type data: dict
        :returns: a dict with keys 'headers' and 'data'"""
        data['nonce'] = self.increment_nonce()

        packed = base64.standard_b64encode(json.dumps(data))
        signature = hmac.new(self.secret, packed, hashlib.sha384).hexdigest()
        return {'headers': {'X-BFX-APIKEY': self.key,
                            'X-BFX-PAYLOAD': packed,
                            'X-BFX-SIGNATURE': signature},
                'data': json.dumps(data)}

    def increment_nonce(self):
        self.nonce = str(int(time.time() * 1e6))
        return self.nonce


def active_orders(auth):
    """:type auth: Auth"""
    return _do_post('orders', auth)


def _do_post(api_call, auth, **opts):
    opts['request'] = '/' + API_VERSION + '/' + api_call
    url = PRIVATE_API_URL + api_call
    return post(url=url,
                **auth.sign(opts))