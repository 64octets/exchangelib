#!/usr/bin/env python


class APIError(IOError):
    """Problem with an API - such as no recent data available"""


class HTTPError(IOError):
    """Problem with an HTTP resonse, such as a 400 code."""
    def __init__(self, message, code=None):
        super(HTTPError, self).__init__(message)
        self.code = code


class ConnectionError(IOError):
    """Problem with the connection, such as a timeout."""