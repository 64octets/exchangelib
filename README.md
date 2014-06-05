Introduction
=====
This package endeavours to provide a consistent interface in Twisted Python to a variety of Bitcoin APIs, starting
with exchanges.

Version: 1.2.0 alpha.

Files & Packages
=====
* `bitcoinapis` is a package containing code that directly interfaces with exchanges.
    * `bitstamp` modules related to the Bitstamp exchange.
        * `websocket` is an interface to Bitstamp's Pusher websocket data API.
        * `observer` WIP, observers are meant to provide a consistent way to see exchange data.
        * `http_data` provides access to the HTTP public API.
        * `http_trade` is a stub, but would eventually implement the Bitstamp trade/private API.
    * `http_api` provides a base class for HTTP APIs.
    * `interfaces` abstracts data types like `Trade` and `OrderBook`.
    * `utils` is a handful of helper functons.

Future Plans
=====
* Add Bitstamp trade api (I don't have a verified Bitstamp account so cannot do this currently)
* Think of a better name

Todo
=====
* parse responses to decimal (as well as data sent on trade apis)
* rate limiting
* tests (live and not)
* standardized objects for return values
* more options (at least proxies)
* response delay/timeout tracking/api connection health indicator
* callbacks for all apis, which would entail polling for http apis (at least optionally)
* cohesive interface for stuff like ticker/orderbook/trades (incl. params like pair)
    * alternatively, could use a `poll` function

* rethink 'interfaces' (all datatypes, too heavyweight)? move to datatypes.py?
* pypubsub or pydispatch for observers

* first order of business: get the bitstamp observer working well.

* make it clearer that this is about bitcoin exchange APIs and not * APIs
* collapse individual exchanges into main package with 1 file per exchange?
* handle TimeoutError/ConnectError properly (lots of these with Huobi)

Changelog
======
1.2.0
* Add preliminary support for Bitfinex, BTC-E, and Huobi