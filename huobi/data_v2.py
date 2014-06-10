# !/usr/bin/env python

import logging
import datetime
import pytz
import calendar
from zope.interface import moduleProvides

from exchangelib.interfaces import IDataAPI
from exchangelib.utils import get_json
from exchangelib import schemas, simpleschema

log = logging.getLogger(__name__)
moduleProvides(IDataAPI)

__all__ = ['ticker', 'orderbook', 'trades', 'candlestick', 'detail']

PAIRS = ['btccny', 'ltccny']
DATA_API_URL = "https://market.huobi.com/staticmarket/"

# Example failure:
# Failure: twisted.internet.error.TimeoutError: User timeout caused connection failure.


@simpleschema.returns(schemas.Ticker)
def ticker(pair='btccny'):
    def process(data):
        data.update(data['ticker'])
        data.pop('ticker')
        return data
    d = get_json(url=_create_url('ticker', pair)).addCallback(process)
    d.addCallback(simpleschema.remap, {'time': 'timestamp', 'buy': 'bid',
                                       'sell': 'ask', 'vol': 'volume'})
    return d


@simpleschema.returns(schemas.OrderBook)
def orderbook(pair='btccny'):
    def process(data):
        data['bids'] = [{'price': price, 'amount': amount} for price, amount in data['bids']]
        data['asks'] = [{'price': price, 'amount': amount} for price, amount in data['asks']]
        return data
    return get_json(url=_create_url('depth', pair)).addCallback(process)


# Huobi doesn't really have a trades API call, it's just emulated using detail()
def trades(pair='btccny'):
    return detail(pair).addCallback(lambda details: details['trades'])


# TODO:
# what is 'amp'??? What are the open/close?
# should direction be true/false or what?
# move _convert_detail_trades back in here?
@simpleschema.returns(schemas.HuobiMarketDetails)
def detail(pair='btccny'):
    def process(data):
        data.pop('top_buy')
        data.pop('top_sell')
        data['trades'] = _convert_detail_trades(data['trades'])
        return data

    d = get_json(url=_create_url('detail', pair))
    d.addCallback(simpleschema.remap, {'p_new': 'last', 'p_open': 'open', 'p_last': 'close',
                                       'p_high': 'high', 'p_low': 'low', 'amount': 'volume',
                                       'total': 'basis_volume', 'level': 'change_pct',
                                       'sells': 'asks', 'buys': 'bids'})
    return d.addCallback(process)


# todo consider renaming to ohlc
# todo convert 't' to real timestamps (original like 't': u'20141106033000000')
#    YYYYMMDDHHMMSS
@simpleschema.returns(schemas.OHLCDataList)
def candlestick(pair='btccny', period='15m'):
    period_translations = {'1m': '001', '5m': '005', '15m': '015', '30m': '030',
                           '60m': '060', '1d': '100', '1w': '200', '1mo': '300', '1y': '400'}
    if period not in period_translations:
        raise ValueError
    url = DATA_API_URL + _convert_pair(pair) + '_kline_' + period_translations[period] + '_json.js'

    def process(data):
        return [{'t': c[0], 'open': c[1], 'high': c[2], 'low': c[3], 'close': c[4], 'volume': c[5]} for c in data]
    return get_json(url=url).addCallback(process)


def ohlc(pair='btccny', period='15m'):
    return candlestick(pair, period)


def _convert_detail_trades(tradelist):
    # need to process the 'time' and 'type' keys on each trade.
    # 'time': string like "01:28:35"
    # 'type': buy/sell in chinese
    now_localized = datetime.datetime.now(tz=pytz.timezone('Asia/Hong_Kong'))

    for trade in tradelist:
        if trade['type'] == u'\u4e70\u5165':
            # buy
            trade['type'] = True
        elif trade['type'] == u'\u5356\u51fa':
            # sell
            trade['type'] = False

        partial_dt = datetime.datetime.strptime(trade['time'], '%H:%M:%S')
        time_localized = now_localized.replace(hour=partial_dt.hour, minute=partial_dt.minute,
                                               second=partial_dt.second, microsecond=0)
        trade['time'] = calendar.timegm(time_localized.utctimetuple())
        #trade['time'] = _hktime_to_timestamp(trade['time'])
    return simpleschema.remap(tradelist, [{'time': 'timestamp', 'type': 'direction'}])


def _convert_pair(pair):
    """:type pair: str"""
    # just remove cny from the end. Ugly way to do it, I'm sure there is better.
    return pair.rsplit('cny')[0]


def _create_url(api_call, pair):
    return DATA_API_URL + api_call + '_' + _convert_pair(pair) + '_json.js'