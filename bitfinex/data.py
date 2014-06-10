# !/usr/bin/env python

import logging
from zope.interface import moduleProvides

from exchangelib.interfaces import IDataAPI
from exchangelib.utils import get_json
from exchangelib import simpleschema, schemas

log = logging.getLogger(__name__)
moduleProvides(IDataAPI)

__all__ = ['ticker', 'orderbook', 'trades', 'lendbook', 'lends', 'stats', 'pairs', 'pairs_detailed']

PAIRS = ['btcusd', 'ltcbtc', 'ltcusd', 'drkusd', 'drkbtc']
CURRENCIES = ['btc', 'usd', 'ltc']
DATA_API_URL = "https://api.bitfinex.com/v1/"

# todo add support for parameters
# todo possibly remove limit_bids/limit_asks to simplify
    # todo why do i have limit_bids+limit_asks on calls which dont even have bids or asks
# todo make something better with pairs and PAIRS/CURRENCIES


@simpleschema.returns(schemas.Ticker)
def ticker(pair='btcusd'):
    d = get_json(url=_make_url('pubticker', pair))
    return d.addCallback(simpleschema.remap, {'last_price': 'last'})


@simpleschema.returns(schemas.OrderBook)
def orderbook(pair='btcusd', limit_orders=50, group=True, limit_bids=None, limit_asks=None):
    # limit_bids/limit_asks optional, overrides limit_orders
    return get_json(url=_make_url('book', pair))


@simpleschema.returns(schemas.TradeList)
def trades(pair='btcusd', limit_orders=50, timelimit=None, limit_bids=None, limit_asks=None):
    d = get_json(url=_make_url('trades', pair))
    return d.addCallback(simpleschema.remap, [{'tid': 'id'}])


# todo naming of calls below this
# particularly stats

@simpleschema.returns(schemas.LendBook)
def lendbook(currency='usd', limit_orders=50, group=True, limit_bids=None, limit_asks=None):
    # semantically broken to pass currency as pair, but it does what is needed
    return get_json(url=_make_url('lendbook', currency))


@simpleschema.returns(schemas.LendStatsList)
def lends(currency='usd', limit_entries=50, timelimit=None, limit_bids=None, limit_asks=None):
    return get_json(url=_make_url('lends', currency))


@simpleschema.returns(schemas.BitfinexStats)
def stats(pair='btcusd'):
    return get_json(url=_make_url('stats', pair))


def pairs():
    """Get a list of valid pairs."""
    return get_json(url=_make_url('symbols'))


def pairs_detailed():
    """Get a list of valid pairs with additional info on them."""
    return get_json(url=_make_url('symbols_details'))


def _make_url(api_call, pair=None):
    url = DATA_API_URL + api_call
    if pair:
        url += '/' + pair
    return url