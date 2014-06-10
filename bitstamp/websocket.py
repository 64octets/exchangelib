#!/usr/bin/env python

import logging
import time
import json
from decimal import Decimal

from twistedpusher import Pusher

from exchangelib import schemas, simpleschema
from exchangelib.observable import Observable

log = logging.getLogger(__name__)

##########################################
# version 2: an observable websocket api #
##########################################


class BitstampWebsocketAPI2(Observable):
    APP_KEY = "de504dc5763aeef9ff52"  # Bitstamp's Pusher API key

    def __init__(self):
        super(BitstampWebsocketAPI2, self).__init__()

        # Pusher channels for live trades, order book, and live orders (order changes)
        self.trade_channel = None
        self.orderbook_channel = None
        self.orderchange_channel = None

        # todo consider moving back out to class variable...
        self._pusher = Pusher(BitstampWebsocketAPI2.APP_KEY)

        # moving this back to being an instance variable, instead of class.
        # Initializing _pusher in class (where =None) instead of init makes it blow up spectacularly.
        #if not self._pusher:
        #    BitstampWebsocketAPI2._pusher = twistedpusher.Client(BitstampWebsocketAPI2.APP_KEY)
        #    pass

    # todo switch from time.time to utc
    @simpleschema.returns(schemas.Trade)
    def trade(self, event):
        data = json.loads(event.data, parse_float=Decimal)
        data['timestamp'] = time.time()
        return data

    @simpleschema.returns(schemas.OrderBook)
    def orderbook(self, event):
        book = dict()
        book['bids'] = [{'price': pr, 'amount': amt} for pr, amt in event.data['bids']]
        book['asks'] = [{'price': pr, 'amount': amt} for pr, amt in event.data['bids']]

        return book

    @simpleschema.returns(schemas.BitstampOrderChange)
    def orderchange(self, event):
        change = event.data
        if event.name == 'order_created':
            kind = 'created'
        elif event.name == 'order_deleted':
            kind = 'deleted'
        elif event.name == 'order_changed':
            kind = 'changed'
        else:
            return

        change['change'] = kind
        change['order_type'] = 'ask' if bool(int(change['order_type'])) else 'bid'

        return simpleschema.remap(change, {'datetime': 'timestamp', 'order_type': 'direction'})

    def hook_listen(self, method_name, listener, is_first=False):
        methods = {'trade', 'orderbook', 'orderchange'}
        if is_first and method_name in methods:
            if method_name == 'trade':
                self.trade_channel = self._pusher.subscribe('live_trades')
                self.trade_channel.bind('trade', self.trade)
            elif method_name == 'orderbook':
                self.orderbook_channel = self._pusher.subscribe('order_book', json_data=True)
                self.orderbook_channel.bind('data', self.orderbook)
            elif method_name == 'orderchange':
                self.orderchange_channel = self._pusher.subscribe('live_orders', json_data=True)
                self.orderchange_channel.bind_all(self.orderchange)


def main():
    import twisted.python.log

    obs = twisted.python.log.PythonLoggingObserver()
    obs.start()
    logging.basicConfig(level=logging.DEBUG)

    api = BitstampWebsocketAPI2()

    def inform(trade):
        print('{:<8d}{:<6.2f} @ ${:.2f}'.format(trade['id'], trade['amount'], trade['price']))
    api.listen('trade', inform)

    def inform_order(order):
        print('{:<8}{:<6.2f} @ ${:<10.2f}{}'.format(order['change'], order['amount'], order['price'], order['timestamp']))
    api.listen('orderchange', inform_order)

    from twisted.internet import reactor
    reactor.run()


if __name__ == '__main__':
    main()
