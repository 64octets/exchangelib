#!/usr/bin/env python

import logging

from bitcoinapis.http_api import PublicHTTP_API

log = logging.getLogger(__name__)

PAIRS = ['btcusd', 'ltcusd', 'ltcbtc', 'drkusd', 'drkbtc']
CURRENCIES = ['btc', 'usd', 'ltc']


# todo option to verify specified pairs against current bitfinex ones using the pairs method
# could also use it to generate list of currencies?
# todo better way to handle api parameters in _get, e.g. CMD/{symbol} or CMD?opt=True
# todo consider breaking limit_orders into limit_bids and limit_asks
class BitfinexDataAPI(PublicHTTP_API):
    API_URL = "https://api.bitfinex.com/v1/"

    @classmethod
    def ticker(cls, pair='btcusd'):
        return cls._get('pubticker/{}'.format(pair))

    @classmethod
    def stats(cls, pair='btcusd'):
        """
        stats/pair
        1d, 7d, 30d volume statistics
        """
        return cls._get('stats/{}'.format(pair))

    @classmethod
    def orderbook(cls, pair='btcusd', limit_orders=50, group=True):
        """"""  # todo opts
        return cls._get('book/{}'.format(pair))

    @classmethod
    def trades(cls, pair='btcusd', limit_trades=50, timelimit=None):
        """"""  # todo opts
        return cls._get('trades/{}'.format(pair))

    @classmethod
    def pairs(cls):
        """Returns a list of valid pairs."""
        return cls._get('symbols')

    @classmethod
    def lends(cls, currency='usd', limit_trades=50, timelimit=None):
        """"""  # todo opts
        return cls._get('lends/{}'.format(currency))

    @classmethod
    def lendbook(cls, currency='usd', limit_orders=50, timelimit=None):
        """"""  # todo opts
        return cls._get('lendbook/{}'.format(currency))
