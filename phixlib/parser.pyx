# -*- coding: utf-8 -*-
'''
phixlib.parser
~~~~~~~~~~~~~~

This module contains a `parse_message` function for parsing a FIX
message into a dict of keys and values. The parser is intelligent
enough to determine the SOH byte (last byte of the message). The
parser attempts to determine the FIX version it is working with based
on the BeginString, falling back to the FIX version supplied in
*version* (default is FIX.4.2).

If you know the message type before hand, you can specify a *cls*
parameter to `parse_message` to force parsing as that message.

'''
from . import FIX
from .fix import Field, Group


__all__ = ['parse_message']


def parse_message(message, cls=None, version='FIX.4.2'):
    '''
    Parse a FIX message as a string into dict of field names and values.

    Automatically determines the field delimiter by looking at the last
    byte of the message.

    Note, there's only so much we can do to parse a really fuzzed up
    message. If you've fuzzed this message beyond recognition,
    serialize the object to json or pickle it before discarding so you
    may recover it.

    :param message: The FIX string you want to parse. Note, the last
        byte of the message must be the field delimiter in order for
        the message to be parsed correctly.

    :param cls: A FIX.FIXMessage class to parse this message as. If
        `None`, the parser will attempt to determine based on the
        `version` and value of the MsgType field (35=) in the message.
        Use this if you're expected to parse a badly formatted message.

    :param version: FIX version to fallback to if it cannot be parsed
        from the BeginString, or the version is not registered in the
        FIX Registry.
    '''

    start = idx = 0
    parts = {}

    soh = message[-1]   # could be \001, |, ^...

    mlen = len(message)
    find = message.find   # optimize attribute lookup

    # parse out BeginString so we know what we're working with

    fix = FIX[version]

    if message[:2] == '8=':
        idx = 2
        end = find(soh, idx)
        value = message[idx:end]

        fix = FIX.get(value, fix)

        parts['BeginString'] = value
        start = end + 1

    if cls:
        _all = cls._all

    field_length = 0
    group = None
    stack = []
    fidx = -1

    while start < mlen and end > -1:

        # between start and idx lies our tag number
        # between idx and end lies our tag value

        idx = find('=', start)
        number = message[start:idx]

        # get the number following the very last soh

        number = number[number.rfind(soh) + 1:]

        end = find(soh, idx + field_length + 1)
        value = message[idx + 1:end]
        start = end + 1

        #print idx, end, start

        # if there's no number or value (i.e., \001=\001)
        # just skip it

        if not number and not value:
            continue

        if not number.isdigit():
            start = idx + 1
            continue

        try:
            field = fix.Fields[number]
            field_length = int(value) if field.type == 'LENGTH' and number != '9' and value.isdigit() else 0
        except KeyError:
            # needs testing
            field = make_field(number)

        # get the Message class based on the value

        if not cls and number == '35':
            cls = fix.Messages.get(value, FIX.FIXMessage)
            _all = cls._all or fix

        if cls and field.name in _all:
            field = _all[field.name]

        #   States:
        #
        #   1. regular field
        #   2. start of repeating group
        #   3. field in repeating group
        #   3a. start of new group within repeating group
        #   4. start of nested repeating group
        #   5. field in nested repeating group

        if stack and field.name in stack[-1]._all:
            field = stack[-1]._all[field.name]

        #print 'parsed', field.name, repr(value), issubclass(field, Group)

        if not group and issubclass(field, Group):
            #print 'start of new group', field.name
            group = parts.setdefault(field.name, [])
            group.append({})
            stack.append(field)
            field_order = field._all.keys()
            #print group, stack
            continue

        elif group and issubclass(field, Group):
            #print group

            if field.name in stack[-1]._all:
                group[-1].setdefault(field.name, []).append({})
            else:
                #print 'clearing stack'
                stack = []
                group = parts.setdefault(field.name, [])
                group.append({})

            stack.append(field)
            field_order = field._all.keys()
            fidx = -1
            #print group, stack
            continue

        elif group and len(stack) == 1:
            if field.name in stack[-1]._all:

                # if the field appears before the last parsed field
                # in the repeating group, then we start a new field

                if field_order.index(field.name) <= fidx:
                    #print 'starting new group'
                    group.append({})

                group[-1][field.name] = value
                fidx = field_order.index(field.name)
                continue

            else:
                _ = stack.pop()
                #print 'exiting repeating group', _.name
                fidx = -1
                if not stack:
                    group = None
                # we exited the repeating group, pass through

        elif group and len(stack) > 1:
            if field.name in stack[-1]._all:

                if field_order.index(field.name) <= fidx:
                    #print 'starting new nested group'
                    group[-1][stack[-1].name].append({})

                group[-1][stack[-1].name][-1][field.name] = value
                fidx = field_order.index(field.name)
                continue

            broke = 0
            while stack:
                _ = stack.pop()
                field_order = stack[-1]._all.keys()

                #print 'exited nested repeating group', _.name

                if stack and field.name in field_order:
                    #print 'adding field to outer group', stack[-1].name
                    if field_order.index(field.name) <= fidx:
                        group.append({})

                    group[-1][field.name] = value
                    fidx = field_order.index(field.name)
                    broke = 1
                    break

                elif stack:
                    # this is reached once a repeating group and nested
                    # repeating group terminate
                    #print 'in break'
                    group = None
                    stack = []
                    break

            # this occurs when we're exiting a nested repeating group
            # before the outer group ends.

            if broke:
                continue

        #print 'adding field to parts', field.name, repr(value), start
        parts[field.name] = value

    return parts


def make_field(number):
    name = 'Field' + number
    dct = {'name': name, 'number': number, 'type': 'STRING', 'enums': {}}
    return type(name, (Field, ), dct)
