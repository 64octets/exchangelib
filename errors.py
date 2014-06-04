#!/usr/bin/env python


class APIError(IOError):
    """Issue with an API - no recent data etc."""


class HTTPError(IOError):
    """Issue with an HTTP resonse."""