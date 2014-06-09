#!/usr/bin/env python

import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

try:
    from bitcoinapis.bitstamp import BitstampObserver
    from bitcoinapis.bitstamp import BitstampWebsocketAPI2
except ImportError:
    pass