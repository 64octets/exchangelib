#!/usr/bin/env python

import logging
import treq
from decimal import Decimal
from twisted.internet import defer

from bitcoinapis.errors import HTTPError, APIError


log = logging.getLogger(__name__)

# todo add pair data to base api class?


class HTTP_API(object):
    API_URL = NotImplemented

    @classmethod
    @defer.inlineCallbacks
    def _get(cls, api_call, is_json=True, **params):
        """:rtype: defer.Deferred"""
        url = cls._create_url(api_call)
        req = yield treq.get(url, headers=None, params=params)
        if req.code != 200:
            raise HTTPError("Bad status code: %d" % req.code)
        if is_json:
            content = yield treq.json_content(req)
        else:
            content = yield treq.content(req)
        defer.returnValue(content)

    @classmethod
    def _create_url(cls, api_call):
        return cls.API_URL + api_call + '/'

    @staticmethod
    @defer.inlineCallbacks
    def _convert_nums(data, decimal_keys=None, int_keys=None):
        """Convert specific keys in a dict to Decimals and ints.

        :type data: dict or defer.Deferred
        :type decimal_keys: list or set
        :type int_keys: list or set
        """
        decimal_keys = decimal_keys or []
        int_keys = int_keys or []
        data = yield data
        new = {}
        for dkey in decimal_keys:
            new[dkey] = Decimal(data[dkey])
        for ikey in int_keys:
            new[ikey] = int(data[ikey])
        defer.returnValue(new)


class PrivateHTTP_API(HTTP_API):
    def __init__(self, key=None, secret=None):
        self.key = key
        self.secret = secret
        self.nonce = 0

    def _post(self, api_call, **params):
        """"""


class PublicHTTP_API(HTTP_API):
    def ticker(self, **kwargs):
        """what exactly is a ticker? define this better"""
        # todo figure out what a ticker is

    def orderbook(self, **kwargs):
        """:rtype: bitcoinapis.datatypes.OrderBook"""

    def trades(self, **kwargs):
        """:rtype: list[bitcoinapis.datatypes.Trade]"""