#!/usr/bin/env python

import logging
import collections
import functools

from twisted.internet import defer

log = logging.getLogger(__name__)


def remap(data, schema):
    """Change key names in a data structure."""
    if isinstance(schema, dict):
        if not isinstance(data, dict):
            raise TypeError("Expected a dict")
        else:
            for key in data.keys():
                if key in schema:
                    data[schema[key]] = data.pop(key)
            return data
    elif isinstance(schema, list):
        if not isinstance(data, collections.Iterable):
            raise TypeError("Expected a list")
        else:
            new_list = list()
            for item in data:
                new_list.append(remap(item, schema[0]))
            return new_list
    else:
        return data


def validate(data, schema):
    """"""
    if isinstance(schema, dict):
        # todo consider optimizing the actual conversions to check whether the type is already correct
        # '?ASDF' syntax to indicate an optional schema key 'ASDF' was inspired by Valideer

        # schema requires a dict as data
        if not isinstance(data, dict):
            raise TypeError("Expected a dict")

        for k in schema:
            # temp storage to avoid issues with the '?' being removed from k
            schema_item = schema[k]

            # Check if it's an optional key, which are strings starting with '?'
            if isinstance(k, basestring) and k.startswith('?'):
                k = k[1:]
                optional = True
            else:
                optional = False

            if k not in data:
                if not optional:
                    raise ValueError("No key '{}' in data".format(k))
                else:
                    continue

            if isinstance(schema_item, type):
                # todo add try/except here
                data[k] = schema_item(data[k])
            elif isinstance(schema_item, (list, dict)):
                data[k] = validate(data[k], schema_item)
            else:
                raise ValueError("bad schema entry '{}' in key {}".format(schema[k], k))
        # todo check for extra keys in data in a strict mode!
        return data

    elif isinstance(schema, list):
        # todo handle multiple possible schemas for list entries
        if not isinstance(data, collections.Iterable):
            raise TypeError("Expected a list")
        #if len(schema) > 1 or len(schema) <= 0:
        #    raise TypeError("list schemas must only have 1 option currently")

        new_data = list()
        if isinstance(schema[0], type):
            for item in data:
                # todo add try/except here
                new_data.append(schema[0](item))
        elif isinstance(schema[0], (dict, list)):
            for item in data:
                new_data.append(validate(item, schema[0]))
        else:
            raise ValueError("bad schema entry for a list")
        return new_data
    else:
        raise TypeError("Bad schema, expected a list or dict")


# possibly rename this... adapt_result? validate_result?
# todo reconsider this optional-deferred scheme...
def returns(schema, strictness=2):
    def factory(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            ret = func(*args, **kwargs)
            if isinstance(ret, defer.Deferred):
                return ret.addCallback(validate, schema)
            else:
                return validate(ret, schema)
        return wrapper
    return factory
