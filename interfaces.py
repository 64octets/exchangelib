#!/usr/bin/env python

from zope.interface import Interface


class IDataAPI(Interface):
    def ticker(pair='btcusd'):
        """"""

    def orderbook(pair='btcusd'):
        """"""

    def trades(pair='btcusd'):
        """"""