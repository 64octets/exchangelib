#!/usr/bin/env python

import logging
from collections import defaultdict
from functools import wraps

from twisted.internet import task, defer

log = logging.getLogger(__name__)

# todo find a better location for this
VERSION = '1.2.0'


###########################################
##### Observable notes
# https://stackoverflow.com/questions/1904351/python-observer-pattern-examples-tips
# realized that this isn't exactly what i'm looking for, since i want to hook function outputs and not inputs.

# todo pypubsub or pydispatch for observers
# I can't just use pubsub/dispatch for API code because it needs to lazy-load the connection.
# is there any way to do that?
# todo consider adding the possibility to listen to inputs instead of outputs, or even both


class Observable(object):
    def __init__(self):
        self._listeners = defaultdict(set)

    def listen(self, method_name, listener):
        """
        Bind a callable to listen to a method - it gets called with the return value whenever that method is called.
        :type method_name: str
        :raises ValueError: if method_name is not a valid method name, or if listener is not callable.
        """
        if not callable(listener):
            raise ValueError("'{}' is an invalid listener since it is not callable.".format(listener))
        elif not hasattr(self, method_name):
            raise ValueError("{} is not a method".format(method_name))

        method_listeners = self._listeners[method_name]
        """:type: set"""
        method_listeners.add(listener)

        if len(method_listeners) == 1:
            first = True

            # If this is the first listener, then set up the method wrapper

            # method_name verified to exist at top
            method = getattr(self, method_name)

            @wraps(method)
            def method_wrapper(*args, **kwargs):
                # todo should i be ignoring null results from func call?
                result = method(*args, **kwargs)
                if result:
                    for l in method_listeners:
                        l(result)
            # Replace the original method with the wrapper
            setattr(self, method_name, method_wrapper)
        else:
            first = False
        self.hook_listen(method_name, listener, is_first=first)

    def unlisten(self, method_name, listener):
        # todo add :raises: documentation for (un)listen

        # Get any existing listeners
        method_listeners = self._listeners[method_name]
        """:type: set"""

        if method_listeners:
            # Remove the listener
            try:
                method_listeners.remove(listener)
            except KeyError:
                pass
                # todo, valueerror? listener was not bound

            # If this was the last listener, then remove the method wrapper
            if not method_listeners:
                is_last = True
                self._listeners.pop(method_name, None)
                # todo error handling for getattr calls
                method = getattr(self, method_name)
                setattr(self, method_name, method.__wrapped__)
            else:
                is_last = False
            self.hook_unlisten(method_name, listener, is_last=is_last)
        else:
            raise ValueError("No listeners registered for {}".format(method_name))

    def hook_listen(self, method_name, listener, is_first=False):
        """
        Meant to be overriden, called by listen()

        :type method_name: str
        :param is_first: whether this was the first listener added to the method.
        """

    def hook_unlisten(self, method_name, listener, is_last=False):
        """
        Meant to be overriden, called by unlisten()

        :type method_name: str
        :param is_last: whether the last listener for this method was just removed.
        """


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
