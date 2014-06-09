# !/usr/bin/env python

import logging
from zope.interface import moduleProvides

from exchangelib.interfaces import IDataAPI
from exchangelib.utils import get_json

log = logging.getLogger(__name__)
moduleProvides(IDataAPI)

__all__ = ['ticker', 'orderbook', 'trades', 'candlestick']

PAIRS = ['btccny', 'ltccny']
DATA_API_URL = "https://market.huobi.com/staticmarket/"

# Example failure:
# Failure: twisted.internet.error.TimeoutError: User timeout caused connection failure.
# todo kline


def ticker(pair='btccny'):
    return get_json(url=_create_url('ticker', pair))


def orderbook(pair='btccny'):
    return get_json(url=_create_url('depth', pair))


# todo, this isn't really trades... more like ticker info + some orderbook/trades
def trades(pair='btccny'):
    return get_json(url=_create_url('detail', pair))


def candlestick(pair='btccny'):
    url = DATA_API_URL + 'td_' + _convert_pair(pair) + '.html'
    return get_json(url=url)


def _convert_pair(pair):
    """:type pair: str"""
    # just remove cny from the end. Ugly way to do it, I'm sure there is better.
    return pair.rsplit('cny')[0]


def _create_url(api_call, pair):
    return DATA_API_URL + api_call + '_' + _convert_pair(pair) + '_json.js'