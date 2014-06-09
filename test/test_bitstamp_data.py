# !/usr/bin/env python

from mock import Mock, patch
from twisted.trial import unittest
from zope.interface.verify import verifyObject

from exchangelib import bitstamp
from exchangelib.interfaces import IDataAPI


class DataTestCase(unittest.TestCase):
    def test_implements_data_api(self):
        verifyObject(IDataAPI, bitstamp)

    @patch('treq.request')
    def test_url_generation_with_ticker(self, mock_get):
        """Simple test to ensure URL generation works."""
        correct_url = 'https://www.bitstamp.net/api/ticker/'
        bitstamp.ticker()
        actual_url = mock_get.call_args[0][1]
        self.assertEqual(correct_url, actual_url, "Incorrect URL generated")