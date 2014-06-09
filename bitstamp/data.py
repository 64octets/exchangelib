# !/usr/bin/env python

import logging
from decimal import Decimal
from zope.interface import moduleProvides

from exchangelib.interfaces import IDataAPI
from exchangelib.utils import get_json

log = logging.getLogger(__name__)
moduleProvides(IDataAPI)

__all__ = ['ticker', 'orderbook', 'trades', 'eur_usd']

PAIRS = ['btcusd']
DATA_API_URL = 'https://www.bitstamp.net/api/'


# should move this to bitstamp module? Main reasons over just importing is sharing vars like PAIRS between data/trade
# and exposing moduleProvides, which may not be compelling enough.
# todo module docstring


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
    return get_json(url=_make_url('ticker', pair),
                    decimal_keys=('volume', 'last', 'bid', 'vwap', 'high', 'low', 'ask'),
                    int_keys=('timestamp',))


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
    # todo use get_json decimal_keys instead of this convert function
    # need to support lists in convert_nums first
    def convert(book):
        return {'bids': [(Decimal(price), Decimal(amount)) for price, amount in book['bids']],
                'asks': [(Decimal(price), Decimal(amount)) for price, amount in book['asks']]}
    content = get_json(url=_make_url('order_book', pair),
                       params={'group': int(group)},
                       int_keys=('timestamp',))
                       # decimal_keys={'bids', 'asks'}
    return content.addCallback(convert)


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
    # todo
    data = get_json(url=_make_url('transactions', pair),
                    params={'time': timeframe},
                    decimal_keys=('price', 'amount'),
                    int_keys=('tid', 'date'))

    def convert(tradelist):
        for trade in tradelist:
            trade['id'] = trade.pop('tid')
            trade['timestamp'] = trade.pop('date')
        return tradelist
    data.addCallback(convert)

    return data


def eur_usd():
    """
    Get the Bitstamp EUR/USD conversion rate.

    Keys:
    buy         - conversion rate when buying
    sell        - conversion rate when selling
    """
    return get_json(url=_make_url('eur_usd'),
                    decimal_keys=('buy', 'sell'))


def _make_url(api_call, pair=None):
    return DATA_API_URL + api_call + '/'