## Todo

* more options
    * proxies
* tests (live and not)
* response delay/timeout tracking/api connection health indicator
* pypubsub or pydispatch for observers
* handle TimeoutError/ConnectError properly (lots of these with Huobi)
* port to asyncio and/or vanilla (to make it more of a general python solution)

Exchange data api status:

* Bitstamp  - ok
* Bitfinex  - ok
* BTC-e     - basic
* Huobi     - basic

Future: Coinbase, 796, OKCoin, Huobi real-time, BitVC trade

Data Schemas:
    going with the fast and easy solution: do all the structural/renaming stuff in-function, 
    breaking out to exchange wide utilities if necessary, and only do type conversions in the global schema code.
    Just do the structural massaging and renaming in-function, and use a decorator to remap the data.
    Decorator usage: 
        `adapt_result({'price': Decimal, 'name': str})`
    Right now simpleschema requires types for conversion, I could possibly extend that back to everything callable().
    
    
IMPORTANT: make all this stuff more robust, currently a lot of it assumes usable responses from exchange apis.
e.g. bitstamp/data/orderbook and some finex stuff

* Add a command line utility for getting data, as well as maybe trading etc in the future
* replace the `_make_url` stuff with something better
* add basis currency tracking
* maybe add caching (save for higher level?)
* rename is_buy on trades - maybe bool direction?
* improve interactive with autocomplete + history
* add args to these api calls

## Thoughts

Schema for exchanges like huobi:btc/cny, huobi:btccny, huobi:btc_cny, + maybe some shorthands like huobi or huobi:btc

Main areas of failure for API code that need to be addressed:

1. Unavailable API calls, such as a 404 response (HTTPError)
2. Timeouts, when the response never completes (errback)
3. Infinite redirects (has happened on Bitfinex). Failure is `twisted.web.error.InfiniteRedirection`.
4. API Errors, error messages returned instead of expected results
5. Code errors, such as when an API is updated
    a) one error: ValueError("No JSON object could be decoded") happening on calls where JSON was expected but not returned
6. ResponseNeverReceived / ConnectionDone (timeout)
    
3) and 5.a) occured on June 19 when Bitfinex started prompting for Incapsula captchas on api.bitfinex.com.
    Basically, a redirect to an HTML page. This occurred because of a DDoS.

Testing/verification strategies:

1. generator used to generate a set of unit tests for every API call
		that confirm behaviour. Additionally fill in the gaps where there is 
		extra exchange-specific code.
		Exhaustive list: timeouts, http errors, api errors, basic url validation.
			How can I test non-pathological conditions?
2. live integration tests, including trade api stuff
		then also possible to compare responses with prior ones to check
		for changes in behaviour
3. stored api responses fed to all calls (stored from integration tests)

test subpackage for each exchange + main one that includes a 'common' module

---

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
