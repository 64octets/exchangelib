#!/usr/bin/env python

import logging
import json
import time
from decimal import Decimal

import twistedpusher

from bitcoinapis.datatypes import Trade, Order, OrderBook, BitstampOrderChange
from bitcoinapis import utils

log = logging.getLogger(__name__)


class BitstampWSAPI(object):
    APP_KEY = "de504dc5763aeef9ff52"  # Bitstamp's Pusher API key
    _pusher = None

    def __init__(self):
        # List of callbacks to be called with parsed json order data
        self.trade_listeners = set()
        self.orderbook_listeners = set()
        self.liveorder_listeners = set()

        # Pusher channels for live trades, order book, and live orders (order changes)
        self.trade_channel = None
        self.orderbook_channel = None
        self.liveorder_channel = None

        # Initializing _pusher in class (where =None) instead of init makes it blow up spectacularly.
        if not self._pusher:
            BitstampWSAPI._pusher = twistedpusher.Client(BitstampWSAPI.APP_KEY)
            pass

    def add_trade_listener(self, listener):
        """
        Listener must be a callable. 1 argument passed to it: an interface.Trade object.
        """
        if callable(listener):
            if len(self.trade_listeners) == 0:
                self.trade_channel = BitstampWSAPI._pusher.subscribe('live_trades')
                self.trade_channel.bind('trade', self.on_trade)
            self.trade_listeners.add(listener)
        else:
            raise ValueError("Listener must be a callable")

    def add_orderbook_listener(self, listener):
        """
        Listener must be a callable. 1 argument passed to it: an interface.OrderBook object.
        """
        if callable(listener):
            if len(self.orderbook_listeners) == 0:
                self.orderbook_channel = BitstampWSAPI._pusher.subscribe('order_book')
                self.orderbook_channel.bind('data', self.on_orderbook)
            self.orderbook_listeners.add(listener)
        else:
            raise ValueError("Listener must be a callable")

    def add_liveorder_listener(self, listener):
        """
        Listener must be a callable. 1 argument passed to it: an interface.BitstampOrderChange object.
        """
        if callable(listener):
            if len(self.liveorder_listeners) == 0:
                self.liveorder_channel = BitstampWSAPI._pusher.subscribe('live_orders')
                self.liveorder_channel.bind_all(self.on_liveorder)
            self.liveorder_listeners.add(listener)
        else:
            raise ValueError("Listener must be a callable")

    def on_trade(self, event):
        data = json.loads(event.data)
        data['price'] = Decimal(data['price'])
        data['amount'] = Decimal(data['amount'])
        data['timestamp'] = time.time()
        trade = Trade(data)

        for cb in self.trade_listeners:
            cb(trade)

    def on_orderbook(self, event):
        data = json.loads(event.data)
        book = OrderBook()
        for order in data['bids']:
            book.bids.append(Order(price=Decimal(order[0]), amount=Decimal(order[1])))
        for order in data['asks']:
            book.asks.append(Order(price=Decimal(order[0]), amount=Decimal(order[1])))
        for cb in self.orderbook_listeners:
            cb(book)

    def on_liveorder(self, event):
        # this is required because channel.bind_all currently also includes pusher:subscription_succeeded events.
        if not event.data:
            return
        data = json.loads(event.data)

        if event.name == 'order_created':
            kind = 'created'
        elif event.name == 'order_deleted':
            kind = 'deleted'
        elif event.name == 'order_changed':
            kind = 'changed'
        else:
            return

        data['price'] = Decimal(data['price'])
        data['amount'] = Decimal(data['amount'])
        data['timestamp'] = int(data['datetime'])
        data.pop('datetime')
        data['change'] = kind
        data['side'] = 'ask' if bool(int(data['order_type'])) else 'bid'
        data.pop('order_type')
        change = BitstampOrderChange(**data)

        for cb in self.liveorder_listeners:
            cb(change)


def main():
    import twisted.python.log
    obs = twisted.python.log.PythonLoggingObserver()
    obs.start()
    logging.basicConfig(level=logging.DEBUG)

    api = BitstampWSAPI()

    def inform(trade):
        print('%d %6.2f @ $%.2f' % (trade.id, trade.amount, trade.price))
    api.add_trade_listener(inform)

    def inform_order(order):
        print('%s %6.2f @ %.2f' % (order.change, order.amount, order.price))
        pass
    api.add_liveorder_listener(inform_order)

    from twisted.internet import reactor
    reactor.run()


if __name__ == '__main__':
    main()
