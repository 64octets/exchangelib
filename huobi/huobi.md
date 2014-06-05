Documentation: [HTTP Data](https://www.huobi.com/help/index.php?a=market_help), 
[HTTP Trade](https://www.huobi.com/help/index.php?a=api_help)


HTTP Data
=========
URL `https://market.huobi.com/staticmarket/`

This API is all sorts of messed up.

* All calls end in `_json.js`
* Pairs are specified as `btc` or `ltc` instead of `btccny` and `ltccny`

Calls:

* `ticker` - High/low, last, volume, bid/ask.
* `detail` - Odd mishmash of info, including 15 trades, 10 nearest bid/ask, and some ticker info.
* `kline` - Strange command to get candlestick data, works like btc_kline_005_json.js where 005 is the period.
* `depth` - Orderbook data.

Bonus: http://market.huobi.com/staticmarket/td[_ltc].html for candlestick data.