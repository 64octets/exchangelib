#!/usr/bin/env python

import logging
from decimal import Decimal
from twisted.internet import defer

from bitcoinapis.http_api import PublicHTTP_API
from bitcoinapis.datatypes import OrderBook, Order, Trade
from bitcoinapis.errors import APIError

log = logging.getLogger(__name__)

# see https://www.bitstamp.net/api/
# Bitstamp has a limit of 600 requests per 10min, after which the client can be banned. Respect this.


class BitstampDataAPI(PublicHTTP_API):
    """
    Simple wrapper around the Bitstamp HTTP data API.
    All calls can raise HTTPError and APIError.
    """
    API_URL = 'https://www.bitstamp.net/api/'

    @classmethod
    def ticker(cls):
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
        dec_keys = {'volume', 'last', 'bid', 'vwap', 'high', 'low', 'ask'}
        int_keys = {'timestamp'}

        raw = cls._get('ticker')
        return cls._convert_nums(raw, dec_keys, int_keys)

    @classmethod
    @defer.inlineCallbacks
    def orderbook(cls, group=True):
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
        if group:
            group = 1
        else:
            group = 0
        raw = yield cls._get('order_book', group=group)
        book = OrderBook()
        book.timestamp = int(raw['timestamp'])

        for bid in raw['bids']:
            bid = Order(price=Decimal(bid[0]), amount=Decimal(bid[1]))
            book.bids.append(bid)
        for ask in raw['asks']:
            ask = Order(price=Decimal(ask[0]), amount=Decimal(ask[1]))
            book.asks.append(ask)

        defer.returnValue(book)

    @classmethod
    @defer.inlineCallbacks
    def trades(cls, timeframe='minute'):
        """
        Get recent Bitstamp transactions.
        :param timeframe: time duration to get trades for. Options: 'minute' and 'hour'.
        :type timeframe: str
        :rtype: defer.Deferred

        Keys:
        date        - timestamp of trade
        tid         - transaction ID
        price       - price the trade executed at
        amount      - amount of BTC that the trade executed for
        """
        dec_keys = {'price', 'amount'}
        int_keys = {'tid', 'date'}

        if timeframe != 'minute' and timeframe != 'hour':
            raise ValueError("Invalid timeframe {}: must be minute or hour.", timeframe)

        raw = yield cls._get('transactions', time=timeframe)
        trades = list()

        for trade in raw:
            parsed = yield cls._convert_nums(trade, dec_keys, int_keys)
            parsed['id'] = parsed.pop('tid')
            parsed['timestamp'] = parsed.pop('date')
            trades.append(Trade(**parsed))

        defer.returnValue(trades)

    @classmethod
    def eur_usd_conversion_rate(cls):
        """
        Get the Bitstamp EUR/USD conversion rate.

        Keys:
        buy         - conversion rate when buying
        sell        - conversion rate when selling
        """
        dec_keys = {'buy', 'sell'}
        return cls._convert_nums(cls._get('eur_usd'), decimal_keys=dec_keys)

    @classmethod
    def _get(cls, api_call, is_json=True, **params):
        """:rtype: defer.Deferred"""
        try:
            data = super(BitstampDataAPI, cls)._get(api_call, is_json, **params)
        except ValueError:
            raise APIError("Could not parse API response")

        def _check_error(response):
            """:type response: dict"""
            if type(response) is dict and response.get('error'):
                raise APIError("Bitstamp error: '{}'".format(response['error']))
            else:
                return response
        data.addCallback(_check_error)
        return data