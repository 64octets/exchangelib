# !/usr/bin/env python

import logging

from bitcoinapis.http_api import PublicHTTP_API

log = logging.getLogger(__name__)

# todo add this one http://market.huobi.com/staticmarket/td.html + td_ltc.html
# candlestick data


class HuobiDataAPI(PublicHTTP_API):
    API_URL = 'https://market.huobi.com/staticmarket/'

    @classmethod
    def ticker(cls, pair='btccny'):
        pair = cls._convert_pair(pair)
        return cls._get('ticker_{}'.format(pair))

    @classmethod
    def orderbook(cls, pair='btccny'):
        pair = cls._convert_pair(pair)
        return cls._get('depth_{}'.format(pair))

    @classmethod
    def trades(cls, pair='btccny'):
        """detail doesn't work perfectly for this..."""
        pair = cls._convert_pair(pair)
        return cls._get('detail_{}'.format(pair))

    @staticmethod
    def _convert_pair(pair):
        """:type pair: str"""
        # just remove cny from the end. Ugly way to do it, I'm sure there is better.
        return pair.rsplit('cny')[0]

    @classmethod
    def _create_url(cls, api_call):
        return cls.API_URL + api_call + '_json.js'