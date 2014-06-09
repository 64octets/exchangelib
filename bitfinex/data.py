# !/usr/bin/env python

import logging
from zope.interface import moduleProvides

from exchangelib.interfaces import IDataAPI
from exchangelib.utils import get_json

log = logging.getLogger(__name__)
moduleProvides(IDataAPI)

__all__ = ['ticker', 'orderbook', 'trades', 'lendbook', 'lends', 'stats', 'pairs']

PAIRS = ['btcusd', 'ltcbtc', 'ltcusd', 'drkusd', 'drkbtc']
CURRENCIES = ['btc', 'usd', 'ltc']
DATA_API_URL = "https://api.bitfinex.com/v1/"

# todo add support for parameters
# todo possibly remove limit_bids/limit_asks to simplify
# todo make something better with pairs and PAIRS/CURRENCIES


def ticker(pair='btcusd'):
    return get_json(url=_make_url('pubticker', pair))


def orderbook(pair='btcusd', limit_orders=50, group=True, limit_bids=None, limit_asks=None):
    # limit_bids/limit_asks optional, overrides limit_orders
    return get_json(url=_make_url('book', pair))


def trades(pair='btcusd', limit_orders=50, timelimit=None, limit_bids=None, limit_asks=None):
    return get_json(url=_make_url('trades', pair))


# todo naming of calls below this
# particularly stats

def lendbook(currency='usd', limit_orders=50, group=True, limit_bids=None, limit_asks=None):
    # semantically broken to pass currency as pair, but it does what is needed
    return get_json(url=_make_url('lendbook', currency))


def lends(currency='usd', limit_orders=50, timelimit=None, limit_bids=None, limit_asks=None):
    return get_json(url=_make_url('lends', currency))


def stats(pair='btcusd'):
    return get_json(url=_make_url('stats', pair))


def pairs():
    """Get a list of valid pairs."""
    return get_json(url=_make_url('pairs'))


def _make_url(api_call, pair=None):
    url = DATA_API_URL + '/' + api_call + '/'
    if pair:
        url += pair + '/'
    return url