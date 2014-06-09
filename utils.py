#!/usr/bin/env python

import logging
from decimal import Decimal
import json
import treq
from twisted.internet import task, defer

from exchangelib.errors import HTTPError

log = logging.getLogger(__name__)

# todo find a better location for this
VERSION = '1.3.0'


# todo rethink passing deferred to processor? only reason is error processing...
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

    # a few options could be useful - such as 'now', 'iterations', and 'clock'.

    if not callable(target) or not callable(processor):
        raise ValueError("Target and processor must be callable")

    def run():
        result = defer.maybeDeferred(target, *args, **kwargs)
        processor(result)

    loop = task.LoopingCall(run)
    loop.start(interval)
    return loop


def get_json(url, params=None, decimal_keys=None, int_keys=None):
    """
    GET a URL, parsing it as JSON.

    :param url: the URL to GET
    :type url: str or unicode
    :param params: parameters to pass in the URL
    :type params: dict
    :param decimal_keys: optional list of JSON keys to parse as Decimals
    :type decimal_keys: Iterable
    :param int_keys: optional list of JSON keys to parse as ints
    :type int_keys: Iterable
    """
    return get(url, **(params or {})).addCallback(parse_json, decimal_keys, int_keys)


def post_json(url, params=None, decimal_keys=None, int_keys=None):
    raise NotImplementedError


def get(url, **params):
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
    # todo fix params so it's like post, since treq lets it include headers etc via headers= params= et al
    return _request('get', url, params=params)


def post(url, **kwargs):
    return _request('post', url, **kwargs)


# todo redirect HTTPError to APIError if an errmsg was returned
# todo TimeoutError handling and document what this raises
# todo user agent
def _request(method, url, **kwargs):
    def handle(req):
        if req.code != 200:
            req.content().addCallback(log.debug)
            raise HTTPError("Bad status code: {} for URL '{}'".format(req.code, url))
        else:
            return req.content()
    return treq.request(method, url, **kwargs).addCallback(handle)


def parse_json(data, decimal_keys=None, int_keys=None):
    """Parse a data blob as JSON, using Decimals and optionally converting specific keys to Decimals or ints.

    :param data: the unparsed JSON
    :type data: str or unicode
    :param decimal_keys: keys in the JSON to parse as Decimals, useful if they are formatted as strings
    :type decimal_keys: Iterable
    :param int_keys: keys in the JSON to parse as ints
    :type int_keys: Iterable

    :returns: parsed JSON

    :raises ValueError: if the JSON was unreadable
    """
    def hook(obj):
        return convert_nums(obj, decimal_keys, int_keys)
    return json.loads(data, object_hook=hook, parse_float=Decimal)


def convert_nums(data, decimal_keys=None, int_keys=None):
    """Convert specific keys in a dict to Decimals and ints.

    :type data: dict
    :param decimal_keys: keys whose values should be converted to Decimals
    :type decimal_keys: Iterable
    :param int_keys: keys whose values should be converted to ints
    :type int_keys: Iterable
    """
    # todo make this more robust and handle lists of results like orderbooks
    # make dec/int_keys possible to use as just a string instead of list/tuple-only
    # todo generalize this function further and expose that thru parse_json
    decimal_keys = decimal_keys or ()
    int_keys = int_keys or ()
    for dkey in decimal_keys:
        if dkey in data:
            data[dkey] = Decimal(data[dkey])
    for ikey in int_keys:
        if ikey in int_keys:
            data[ikey] = int(data[ikey])
    return data