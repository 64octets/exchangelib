#!/usr/bin/env python

from zope.interface import Interface


class IDataAPI(Interface):
    def ticker(**kwargs):
        """"""

    def orderbook(**kwargs):
        """"""

    def trades(**kwargs):
        """"""