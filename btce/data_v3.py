#!/usr/bin/env python

from bitcoinapis.http_api import PublicHTTP_API

# See https://btc-e.com/api/3/documentation


# todo standardize pair names to btcusd etc instead of btc_usd
# todo support multi-pair queries
# todo add options
class BtceDataAPIv3(PublicHTTP_API):
    API_URL = 'https://btc-e.com/api/3/'

    @classmethod
    def ticker(cls, pair='btcusd'):
        pair = cls._convert_pair(pair)
        return cls._get('ticker/{}'.format(pair))

    @classmethod
    def orderbook(cls, pair='btcusd', limit_orders=150):
        pair = cls._convert_pair(pair)
        return cls._get('depth/{}'.format(pair), limit=limit_orders)

    @classmethod
    def trades(cls, pair='btcusd', limit_trades=150):
        pair = cls._convert_pair(pair)
        return cls._get('trades/{}'.format(pair), limit=limit_trades)

    @classmethod
    def pair_info(cls, pair='btcusd'):
        # todo naming
        pair = cls._convert_pair(pair)
        return cls._get('info/{}'.format(pair))

    @staticmethod
    def _convert_pair(pair):
        """Converts a pair in standard form (e.g. btcusd) to BTC-E's format of btc_usd."""
        if len(pair) == 6:
            return pair[:3] + '_' + pair[3:]
        else:
            # todo
            pass