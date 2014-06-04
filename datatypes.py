#!/usr/bin/env python

import logging
from collections import namedtuple

log = logging.getLogger(__name__)


class AttributeDict(dict):
    def __init__(self, **kwargs):
        super(AttributeDict, self).__init__(**kwargs)

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, item):
        return self[item]


class Trade(AttributeDict):
    """
    Should have keys: price, amount, timestamp.
    Maybe: id, is_buy
    """


Order = namedtuple('Order', ['price', 'amount'])


BitstampOrderChange = namedtuple('BitstampOrderChange', ['price', 'amount', 'change', 'timestamp', 'id', 'side'])


# todo improve this... will conflict with consolidated orderbook stuff
# Order is good, so is BitstampOrderChange. Trade... I guess it's ok.
class OrderBook(AttributeDict):
    """
    Keys 'bids' and 'asks', containing lists of Orders.
    """
    def __init__(self):
        super(OrderBook, self).__init__()
        self.bids = list()
        self.asks = list()