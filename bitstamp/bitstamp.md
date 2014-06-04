Bitstamp has 2 data APIs, HTTP and websocket through Pusher.

Websocket
=========
Pusher key `de504dc5763aeef9ff52`

Channels:

* live_trades, event `trade`
    Streams orders
* `orderbook`, event `data`
    Streams orderbook. Not very useful, has a nasty habit of not triggering for a while
    (60s+) and is limited to a small number of orders
* live_orders (unofficial), events `order_created`, `order_deleted`, `order_changed`
    All modifications to the entire orderbook

HTTP Data
=========
URL: `https://www.bitstamp.net/api/`

Limited to 600 requests per 10 minutes

Calls:

* `ticker`
    Basic market data (last trade, 24h statistics)
* `order_book`
    Full orderbook
* `transactions`
    Recent trades (last minute or hour)
* `eur_usd`
    Conversion rates


Orderbook Observer Design
========
Will use:

* HTTP orderbook
* Websocket order changes

Operation:

1. Get the HTTP orderbook. Doing so repeatedly should be unnecessary, but can be done infrequently
to provide integrity checks.

2. Modify the orderbook returned by HTTP API with websocket updates

Demo: get http orderbook every 60s. Modify with websocket updates, then verify against new http orderbook.