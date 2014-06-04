#!/usr/bin/env python

import logging
import re
import json

from twisted.internet import defer

from bitcoinapis.http_api import PublicHTTP_API
from bitcoinapis.errors import APIError

log = logging.getLogger(__name__)


# TODO update to new API version released in-place (incidentally breaking most sites...) on Apr. 27, 2014
#https://www.huobi.com/help/index.php?a=market_help

##########################
# Market depth (bids/asks, UNDOCUMENTED).
# depth[_ltc].html

# Data returned FOR BTC:
#       {'marketdepth': [{'name': ---, 'data': [HIGHEST_BID, BID2]}, {'name': ---, 'data': [LOWEST_ASK, ASK2]}]}
# Bids and asks are in list format, as (PRICE, TOTAL_ORDERBOOK_DEPTH, AMOUNT). All 3 are floats/decimal#s.

# Data returned FOR LTC:
#       {'asks': [HIGHEST_ASK, ASK2], 'bids': [LOWEST_BID, BID2]}
# Bids and asks are in list format, as (PRICE, AMOUNT). Note: amount is a float/decimal#, price is
# either a quoted string OR an integer.

##########################

# ticker data (along with recent trades/small orderbook).
# detail[_ltc}.html
# Returned: view_details({INFO_DICT})
# In INFO_DICT: (buys, sells, top_buy, top_sell, trades, ~~~LOTS OF TICKER DATA~~~)
##########################

# todo add this csv data api that returns volumes and avg prices
# 1minute csv data, fields (time_of_day, avg_price, quote_volume, basis_volume)
# td[_ltc].html

##########################

# ohlc data
# periods 001, 005, 015, 030, 060 (x min), 100 (1d), 200 (1w), 300 (1m), 400 (1y)
# kline[_ltc][period].html
##########################


class HuobiDataAPI(PublicHTTP_API):
    API_URL = "https://market.huobi.com/staticmarket/"
    PAIRS = ('ltccny', 'btccny')
    OHLC_PERIODS = {'1m': '001',
                    '5m': '005',
                    '15m': '015',
                    '30m': '030',
                    '60m': '060',
                    '1h': '060',
                    '1d': '100',
                    '1w': '200',
                    '1mo': '300',
                    '1y': '400'}

    # todo caching of detail
    # todo parsing before returning

    def __init__(self):
        """"""

    def orderbook(self, pair='btccny'):
        """"""
        # data returned is in a different format depending on whether it's btc or ltc...
        call = 'depth' + self._pair_str(pair)
        content = self._get(call)

        return content

    def ticker(self, pair='btccny'):
        """:rtype: defer.Deferred"""
        content = self._get_detail(pair)
        return content

    @defer.inlineCallbacks
    def trades(self, pair='btccny'):
        """:rtype: defer.Deferred"""
        content = yield self._get_detail(pair)
        try:
            defer.returnValue(content['trades'])
        except KeyError:
            raise APIError("Could not read trade data from Huobi data API.")

    def ohlc(self, pair='btccny', period='1m'):
        """"""
        try:
            api_period = HuobiDataAPI.OHLC_PERIODS[period]
        except KeyError:
            raise ValueError("Invalid ohlc period: {0}.".format(period))
        call = 'kline' + self._pair_str(pair) + api_period
        return self._get(call)

    def ohlc_periods(self):
        return HuobiDataAPI.OHLC_PERIODS.keys()

    @defer.inlineCallbacks
    def _get_detail(self, pair):
        """:rtype: dict"""
        call = 'detail' + self._pair_str(pair)
        content = yield self._get(call, json=False)
        try:
            content = re.match('view_detail\((.+)\)', content).group(1)
        except AttributeError:
            raise APIError("Unparseable return value from Huobi data api call '{0}'.".format(call))
        else:
            defer.returnValue(json.loads(content))

    def _pair_str(self, pair):
        if pair in HuobiDataAPI.PAIRS:
            if pair == 'ltccny':
                return '_ltc'
            elif pair == 'btccny':
                return ''
        raise ValueError("No such trading pair on Huobi.")

    def _create_url(self, api_call):
        return super(HuobiDataAPI, self)._create_url(api_call)[:-1] + '.html'


def main():
    import twisted.python.log
    obs = twisted.python.log.PythonLoggingObserver()
    obs.start()
    logging.basicConfig(level=logging.DEBUG)

    def say(msg):
        print(msg)

    api = HuobiDataAPI()
    api.trades().addCallback(say)
    #api.orderbook(group=True).addCallback(say2)

    from twisted.internet import reactor
    reactor.run()


if __name__ == '__main__':
    main()
