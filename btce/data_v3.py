# !/usr/bin/env python

import logging
from zope.interface import moduleProvides

from exchangelib.interfaces import IDataAPI
from exchangelib.utils import get_json
from exchangelib import schemas, simpleschema

log = logging.getLogger(__name__)
moduleProvides(IDataAPI)

__all__ = ['ticker', 'orderbook', 'trades', 'pair_info']

# todo pairs/currencies
PAIRS = ['btcusd']
DATA_API_URL = "https://btc-e.com/api/3/"

# API v3
# todo support multi-pair queries
# todo add options
# todo pull out the pair key e.g. btc_usd


# todo add basis_volume to dec conversion? float so done auto for now
@simpleschema.returns(schemas.Ticker)
def ticker(pair='btcusd'):
    # api fails with code 200 and     {u'error': u'Invalid method', u'success': 0}
    def process(data):
        new = data[_convert_pair(pair)]
        return simpleschema.remap(new, {'buy': 'bid', 'sell': 'ask', 'updated': 'timestamp',
                                        'vol': 'volume', 'vol_cur': 'basis_volume', 'avg': 'mid'})
    return get_json(url=_make_url('ticker', pair)).addCallback(process)


@simpleschema.returns(schemas.OrderBook)
def orderbook(pair='btcusd', limit_orders=150):
    def process(data):
        new = data[_convert_pair(pair)]
        new['bids'] = [{'price': b[0], 'amount': b[1]} for b in new['bids']]
        new['asks'] = [{'price': a[0], 'amount': a[1]} for a in new['asks']]
        return new
    return get_json(url=_make_url('depth', pair)).addCallback(process)


@simpleschema.returns(schemas.TradeList)
def trades(pair='btcusd', limit_trades=150):
    def process(data):
        new = data[_convert_pair(pair)]
        for trade in new:
            trade['direction'] = bool(trade.pop('type') == 'bid')
        return simpleschema.remap(new, [{'tid': 'id'}])
    return get_json(url=_make_url('trades', pair)).addCallback(process)


# todo naming of this ( + entry in __all__)
# todo this doesnt take a pair
def pair_info(pair='btcusd'):
    return get_json(url=_make_url('info', pair))


def _convert_pair(pair):
    if len(pair) == 6:
        return pair[:3] + '_' + pair[3:]
    else:
        # todo
        raise ValueError("Cannot convert pair {} because it isn't 6 chars".format(pair))


def _make_url(api_call, pair=None):
    return DATA_API_URL + api_call + '/' + _convert_pair(pair) + '/'
