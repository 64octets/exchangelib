#!/usr/bin/env python

import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

try:
    from exchangelib.bitstamp import BitstampObserver
    from exchangelib.bitstamp import BitstampWebsocketAPI2
except ImportError:
    pass