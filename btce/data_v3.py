# !/usr/bin/env python

import logging
from zope.interface import moduleProvides

from bitcoinapis.interfaces import IDataAPI
from bitcoinapis.utils import get_json

log = logging.getLogger(__name__)
moduleProvides(IDataAPI)

__all__ = ['ticker', 'orderbook', 'trades', 'pair_info']

# todo pairs/currencies
PAIRS = ['btcusd']
DATA_API_URL = "https://btc-e.com/api/3"

# API v3
# todo support multi-pair queries
# todo add options


def ticker(pair='btcusd'):
    # api fails with code 200 and     {u'error': u'Invalid method', u'success': 0}
    return get_json(url=_make_url('ticker', pair))


def orderbook(pair='btcusd', limit_orders=150):
    return get_json(url=_make_url('depth', pair))


def trades(pair='btcusd', limit_trades=150):
    return get_json(url=_make_url('trades', pair))


# todo naming of this ( + entry in __all__)
def pair_info(pair='btcusd'):
    return get_json(url=_make_url('info', pair))


def _convert_pair(pair):
    if len(pair) == 6:
        return pair[:3] + '_' + pair[3:]
    else:
        # todo
        raise ValueError("Cannot convert pair {} because it isn't 6 chars".format(pair))


def _make_url(api_call, pair=None):
    return DATA_API_URL + '/' + api_call + '/' + _convert_pair(pair) + '/'
