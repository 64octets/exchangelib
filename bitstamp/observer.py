#!/usr/bin/env python

import logging
import time
from collections import deque


from bitcoinapis import datatypes
from bitcoinapis.bitstamp import websocket

log = logging.getLogger(__name__)

# todo exceptions instead of True/False/None
# todo more consistent event handling/listening/etc.
# https://stackoverflow.com/questions/1092531/event-system-in-python
# http://pubsub.sourceforge.net/
# https://pypi.python.org/pypi/zope.event


class BitstampObserver(object):
    def __init__(self):
        self.api = websocket.BitstampWSAPI()

        self._highestbid = None
        self._lowestask = None

        self.last_orderbook = None
        self._orderbook = None
        self.recent_trades = deque()

        self.trade_listeners = set()

        self.api.add_trade_listener(self.on_trade)
        self.api.add_orderbook_listener(self.on_orderbook)
        self.api.add_liveorder_listener(self.on_order_change)

    @property
    def highestbid(self):
        if self._is_orderbook_fresh():
            return self._highestbid

    @property
    def lowestask(self):
        if self._is_orderbook_fresh():
            return self._lowestask

    @property
    def orderbook(self):
        if self._orderbook and self._is_orderbook_fresh():
            return self._orderbook
        else:
            return datatypes.OrderBook()

    def on_orderbook(self, data):
        """
        Callback, called when new bitstamp orderbook data available.
        :type data: datatypes.OrderBook
        """

        #if 'bids' in data and 'asks' in data and len(data['bids']) > 0 and len(data['asks']) > 0:
        try:
            self._highestbid = data.bids[0].price
            self._lowestask = data.asks[0].price
        except (KeyError, AttributeError, IndexError):
            log.error("Bad orderbook data received", exc_info=True)
        else:
            self._orderbook = data
            self.last_orderbook = time.time()

    def on_trade(self, data):
        """
        Callback, called when new bitstamp trade events
        Data persisted in self.recent_trades.
        :type data: datatypes.Trade
        """
        self._determine_trade_direction(data)
        if not 'is_buy' in data:
           # short circuit if not tagged as buy or sell
            return
        else:
            self.recent_trades.appendleft(data)
            for cb in self.trade_listeners:
                pass

    def on_order_change(self, data):
        """
        :type data: datatypes.OrderChange
        """
        try:
            if self.orderbook.bids[-1].price < data.price < self.orderbook.asks[-1].price:
                #log.info("got a change, %s" % (data, ))
                pass
            #todo update orderbook with this info
        except (IndexError, AttributeError):
            pass

    def add_trade_listener(self, listener):
        if callable(listener):
            self.trade_listeners.add(listener)
        else:
            raise ValueError("Listener must be a callable")

    def _is_orderbook_fresh(self):
        """
        Check that the orderbook data is fresh.
        Returns true if it is, or there isn't data, and false if it's stale.
        :rtype: bool
        """
        now = time.time()
        if self.last_orderbook and now - self.last_orderbook > 60:
            # 60s+ since last orderbook
            return False
        else:
            # either the orderbook callback hasn't triggered yet or we have fresh data
            return True

    def _determine_trade_direction(self, trade):
        """
        Decides whether a given trade was a buy or sell, based on orderbook data.
        Exists because Bitstamp doesn't say whether an executed trade is a bid or an ask.
        :type trade: datatypes.Trade
        """
        bid = self.highestbid
        ask = self.lowestask
        # todo change 'is_buy' bool to 'type' string 'bid' | 'ask'
        if not bid or not ask:
            return

        if trade.price <= bid:
            # order executed under or at bid, so it's a sell
            trade.is_buy = False
        if trade.price >= ask:
            # order executed at or above ask, so it's a buy
            trade.is_buy = True


#####################

def main():
    from twisted.internet import reactor, task
    import twisted.python.log
    obs = twisted.python.log.PythonLoggingObserver()
    obs.start()

    logging.basicConfig(level=logging.DEBUG)

    obs = BitstampObserver()

    def inform():
        if len(obs.orderbook.bids) > 0:
            try:
                print("Highest bid %.2f, lowest ask %.2f; lowest bid %.2f and highest ask %.2f." %
                      (obs.highestbid, obs.lowestask, obs.orderbook.bids[-1].price, obs.orderbook.asks[-1].price))
                pass
            except TypeError as e:
                log.debug("Error: {0}".format(e.message))
    loop = task.LoopingCall(inform)
    loop.start(3)

    reactor.run()


if __name__ == '__main__':
    main()
