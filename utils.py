#!/usr/bin/env python

import logging
from decimal import Decimal
import json
import treq
from twisted.internet import task, defer

from exchangelib.errors import HTTPError
from exchangelib.version import VERSION

log = logging.getLogger(__name__)


def poll(interval, target, processor, *args, **kwargs):
    """
    Run a function at intervals and process the results with another function.

    :param interval: how long to wait between calls of target, in seconds
    :type interval: int or float
    :param target: function to run, invoked with args and kwargs
    :param processor: function that receives Deferreds which fire with target's return value and exceptions

    :returns: an object with a method stop() that can be used to halt the polling early
    :rtype: LoopingCall

    :raises ValueError: if target or processor are not callable
    """
    # todo rethink passing deferred to processor? only reason is error processing...
    # a few options could be useful - such as 'now', 'iterations', and 'clock'.

    if not callable(target) or not callable(processor):
        raise ValueError("Target and processor must be callable")

    def run():
        result = defer.maybeDeferred(target, *args, **kwargs)
        processor(result)

    loop = task.LoopingCall(run)
    loop.start(interval)
    return loop


def get_json(url, params=None,  **kwargs):
    """
    GET a URL, parsing it as JSON.

    :param url: the URL to GET
    :type url: str or unicode
    :param params: parameters to pass in the URL
    :type params: dict
    """
    return get(url, params, **kwargs).addCallback(parse_json)


def post_json(url, params=None):
    raise NotImplementedError


def get(url, params=None, **kwargs):
    """
    GET a URL.

    :param url: an API URL to GET
    :type url: str or unicode
    :param params: parameters to pass in the URL
    :type params: dict

    :returns: the pages content
    :rtype: defer.Deferred

    :raises HTTPError: via errback if the GET was unsuccessful
    """
    params = params or {}
    return _request('get', url, params=params, **kwargs)


def post(url, **kwargs):
    return _request('post', url, **kwargs)


# todo redirect HTTPError to APIError if an errmsg was returned
# todo TimeoutError handling and document what this raises
# todo tune timeout
def _request(method, url, **kwargs):
    def handle(req):
        if req.code != 200:
            req.content().addCallback(log.debug)
            raise HTTPError("Bad status code: {} for URL '{}'".format(req.code, url))
        else:
            return req.content()

    # set the User-Agent header if it isn't already set by the user
    if 'headers' not in kwargs:
        kwargs['headers'] = {}
    if 'User-Agent' not in kwargs['headers']:
        kwargs['headers']['User-Agent'] = 'exchangelib/{}'.format(VERSION)

    return treq.request(method, url, **kwargs).addCallback(handle)


# todo remove
def parse_json(data):
    """Parse a data blob as JSON.

    :param data: the unparsed JSON
    :type data: str or unicode
    :returns: parsed JSON

    :raises ValueError: if the JSON was unreadable
    """
    return json.loads(data, parse_float=Decimal)
