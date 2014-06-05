[Existing implementation](https://github.com/alanmcintyre/btce-api) (MIT license)

Documentation: 
[v2 (v1?)](https://btc-e.com/api/documentation), 
[v3 (Russian only)](https://btc-e.com/api/3/documentation)


v3 HTTP Data
============

URL: `https://btc-e.com/api/3/`

Can use API calls with multiple pairs separated by dashes. Pairs are separated with underscores, e.g. `btc_usd`.

Everything is cached for 2s, querying faster than that is pointless. `ignore_invalid` can be used to ignore bad
pair names in API calls, otherwise it raises an error - this seems mostly useful for multi-pair calls.

Calls:

* `info` - cannot be used with multiple pairs. Info on fees, min/max prices, min trade, \# of decimal places.
* `ticker` - basic stats on the pair, such as last, bid/ask, high/low/volume (what timeframe?)
* `depth` - orderbook. Default 150 bid/ask, maximum 2000 using `limit` param.
* `trades` - recent trades. Default last 150, maximum 2000 using `limit` param. Differentiates between bid/ask
and has transaction IDs.