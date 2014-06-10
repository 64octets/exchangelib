Introduction
=====
Exchangelib provides a consistent interface in Python to Cryptocurrency exchange APIs, initially focusing
on Bitcoin.

Note that it currently requires using Twisted.

Version: 1.3.1 alpha.

Requirements: Python 2.7, `Twisted`, `Treq`, and `Twistedpusher`.

Example
=======
    import pprint
    from exchangelib import bitstamp
    
    ticker = bitstamp.ticker()
    ticker.addCallback(pprint.pprint)

Files & Packages
================
* `interactive.py` is a simple REPL that can be used to query APIs 

Future Plans
=====
* Add Bitstamp trade api (issue: no verified Bitstamp account to test it with)

Changelog
======
1.3.1
* Add `simpleschema` (and `schemas`)
* Add `forex`, a module to do currency conversions
* OK support for Bitfinex, Bitstamp, BTC-E, Huobi data APIs
* Various bugfixes 
    - interactive is no longer limited to a subset of API calls
    - user-agent headers passed on HTTP requests

1.3.0
* Revamp API design to make them easier to use (no separate classes)
* Working authentication code for Bitfinex

1.2.0
* Add preliminary support for Bitfinex, BTC-E, and Huobi