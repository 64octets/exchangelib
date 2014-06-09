# !/usr/bin/env python

from twisted.trial import unittest
from zope.interface.verify import verifyObject

from bitcoinapis.bitstamp import data
from bitcoinapis.interfaces import IDataAPI


class DataTestCase(unittest.TestCase):
    def test_implements_data_api(self):
        verifyObject(IDataAPI, data)
