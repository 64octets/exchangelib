#!/usr/bin/env python

import logging

from bitcoinapis.http_api import PublicHTTP_API

log = logging.getLogger(__name__)


class BitfinexDataAPI(PublicHTTP_API):
    API_URL = "https://api.bitfinex.com/v1/"

    def __init__(self):
        """"""

    def ticker(self, pair='btcusd'):
        """"""

    def orderbook(self, pair='btcusd'):
        """"""

    def today(self, pair='btcusd'):
        """"""

    def trades(self, pair='btcusd', limit_trades=50, timelimit=None):
        """"""

    def pairs(self):
        """"""

    def lends(self):
        """"""

    def lendbook(self, currency='usd', limit_trades=50):
        """"""


def main():
    pass


if __name__ == '__main__':
    main()
