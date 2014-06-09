Introduction
=====
This is a project to provide a consistent interface to a variety of Bitcoin exchange APIs in Python.

Note that it currently requires Twisted.

Version: 1.3.0 alpha.

Files & Packages
=====
* `exchangelib` is a package containing code that directly interfaces with exchanges.
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
* Add Bitstamp trade api (issue: no verified Bitstamp account to test it with)

Todo
=====
* more options
    * proxies
* update readme, particularly module/package list
    * note that rate limits etc are not enforced on bare apis
* tests (live and not)
* response delay/timeout tracking/api connection health indicator
* pypubsub or pydispatch for observers
* make it clearer that this is about bitcoin exchange APIs and not * APIs
* handle TimeoutError/ConnectError properly (lots of these with Huobi)
* port to asyncio and/or vanilla (to make it more of a general python solution)

Exchange data api status:

* Bitstamp  - ok
* Bitfinex  - basic
* BTC-e     - basic
* Huobi     - basic

Future: Kraken, Vault of Satoshi, Mintpal

* improve decimal/int conversion
* Dynamically generate API call functions

* remove/replace exchangelib.datatypes (currently used only by bitstamp.websocket) 

Thoughts
========
Schema for exchanges like huobi:btc/cny or something similar?

Main areas of failure for API code that need to be addressed:

1. Unavailable API calls, such as a 404 response (HTTPError)
2. Timeouts, when the response never completes (errback)
3. API Errors, error messages returned instead of expected results
4. Code errors, such as when an API is updated

Testing/Verification Strategy: both live and not, store results of live ones to check for changes later.
 Tests for all exchanges should be basically the same.

Exchange package setup (examples using bitstamp):

- public api calls are direct (bitstamp.ticker)
- streaming api is available as Streaming (bitstamp.Streaming)
- observer is available as Observer(bitstamp.Observer)
- Private API is direct (bitstamp.make_trade), with authentication done using an 
    Auth class (bitstamp.Auth), that is passed to the private api calls. 
    This can be extended to set a default auth info and similar.
- a special exchange named 'all' that gets data for all exchanges

Exchange data interfaces:

1. Direct, call a method and make the api call
    This one is very straightforward, at least if 100% compatible exchanges are not required.
2. Push, where data is sent to listeners (pypubsub)
    Trades are easily retrieved with this, but what about orderbooks and tickers?
3. Pull, where data is updated and can be fetched at any time
4. Arbitrary polling, as a form of \#2?

note: \#2 and \#3 can be provided by the same class.

Trading/Account interfaces:

1. Direct, single-exchange only
2. Managed, for easily trading on multiple exchanges or with multiple accounts
    This will also handle account-specific data like trading logs and everything else in the private api.
3. Watch, read-only push-type access to monitor stuff like trade activity, open positions, etc. 
    Possibly not needed, in which case it is rolled into Managed.

Changelog
======
1.3.0
* Revamp API design to make them easier to use (no separate classes)
* Working authentication code for Bitfinex
1.2.0
* Add preliminary support for Bitfinex, BTC-E, and Huobi