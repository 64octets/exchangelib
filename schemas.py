#!/usr/bin/env python

import logging
from decimal import Decimal

log = logging.getLogger(__name__)

# todo replace XList with [X] in actual schema usages? No drawback unless I'm adding more to these eventually

# todo replace 'is_buy' with 'direction'? That is currently used in OrderChange
Trade = {'price': Decimal, 'amount': Decimal, 'timestamp': int, '?id': int, '?is_buy': bool}
TradeList = [Trade]

# timestamp in Order is a decimal because int doesn't work with finex, since e.g. int('1234859435.0') means exception
# could do a datetime or whatever instead
Order = {'price': Decimal, 'amount': Decimal, '?timestamp': Decimal}
OrderList = [Order]

OrderBook = {'bids': [Order], 'asks': [Order], '?timestamp': int}

Ticker = {'high': Decimal, 'low': Decimal, '?mid': Decimal,
          'bid': Decimal, 'ask': Decimal, 'last': Decimal,
          'volume': Decimal, 'timestamp': Decimal, '?vwap': Decimal}

ConversionRate = {'buy': Decimal, 'sell': Decimal}

OHLCData = {'open': Decimal, 'high': Decimal, 'low': Decimal, 'close': Decimal, 'volume': Decimal, '?timestamp': int}
OHLCDataList = [OHLCData]

#####################
# Exchange-specific #
#####################

HuobiMarketDetails = {'last': Decimal, 'open': Decimal, 'close': Decimal, 'high': Decimal, 'low': Decimal,
                      'volume': Decimal, 'basis_volume': Decimal, 'change_pct': Decimal,
                      'bids': [Order], 'asks': [Order], 'trades': TradeList}

BitstampOrderChange = {'change': str, 'price': Decimal, 'amount': Decimal, 'timestamp': int, 'direction': str}

# These are only for Bitfinex, might want to rename
LendStats = {'amount_lent': Decimal, 'rate': Decimal, 'timestamp': int}
LendStatsList = [LendStats]
LendOffer = {'amount': Decimal, 'frr': bool, 'period': int, 'rate': Decimal, 'timestamp': Decimal}
LendBook = {'bids': [LendOffer], 'asks': [LendOffer], '?timestamp': int}

BitfinexStats = [{'period': int, 'volume': Decimal}]
