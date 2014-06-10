# !/usr/bin/env python

import logging
from decimal import Decimal
from zope.interface import moduleProvides

from exchangelib.interfaces import IDataAPI
from exchangelib.utils import get_json
from exchangelib import simpleschema, schemas

log = logging.getLogger(__name__)
moduleProvides(IDataAPI)

__all__ = ['ticker', 'orderbook', 'trades', 'eur_usd']

PAIRS = ['btcusd']
DATA_API_URL = 'https://www.bitstamp.net/api/'


# should move this to bitstamp module? Main reasons over just importing is sharing vars like PAIRS between data/trade
# and exposing moduleProvides, which may not be compelling enough.
# todo module docstring


@simpleschema.returns(schemas.Ticker)
def ticker(pair='btcusd'):
    """
    Get the Bitstamp ticker, which includes data on the last 24 hours.

    :rtype: defer.Deferred

    Keys:
    timestamp   - time the data was generated
    volume      - 24h volume
    vwap        - 24h volume-weighted average price
    bid         - highest bid
    ask         - lowest ask
    last        - last trade price
    low         - lowest price in last 24h
    high        - highest price in last 24h
    """
    return get_json(url=_make_url('ticker', pair))


@simpleschema.returns(schemas.OrderBook)
def orderbook(pair='btcusd', group=True):
    """
    Get the full Bitstamp orderbook.

    :param group: whether to group orders with the same price.
    :type group: bool
    :rtype: defer.Deferred

    Keys:
    bids        - list of bids
    asks        - list of asks
    timestamp   - when the orderbook data was created/returned
    """
    raw = get_json(url=_make_url('order_book', pair),
                   params={'group': int(group)})

    def reflow(book):
        book['bids'] = [{'price': b[0], 'amount': b[1]} for b in book['bids']]
        book['asks'] = [{'price': a[0], 'amount': a[1]} for a in book['asks']]
        return book
    return raw.addCallback(reflow)


@simpleschema.returns(schemas.TradeList)
def trades(pair='btcusd', timeframe='minute'):
    """
    Get recent Bitstamp transactions.
    :param timeframe: time duration to get trades for. Options: 'minute' and 'hour'.
    :type timeframe: str
    :rtype: defer.Deferred

    :raises ValueError: on invalid timeframe

    Keys:
    date        - timestamp of trade
    tid         - transaction ID
    price       - price the trade executed at
    amount      - amount of BTC that the trade executed for
    """
    valid_timeframes = ('minute', 'hour')
    if timeframe not in valid_timeframes:
        raise ValueError("Invalid timeframe {}", timeframe)
    data = get_json(url=_make_url('transactions', pair),
                    params={'time': timeframe})
    return data.addCallback(simpleschema.remap, [{'tid': 'id', 'date': 'timestamp'}])


@simpleschema.returns(schemas.ConversionRate)
def eur_usd():
    """
    Get the Bitstamp EUR/USD conversion rate.

    Keys:
    buy         - conversion rate when buying
    sell        - conversion rate when selling
    """
    return get_json(url=_make_url('eur_usd'))


def _make_url(api_call, pair=None):
    return DATA_API_URL + api_call + '/'