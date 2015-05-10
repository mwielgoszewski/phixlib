# -*- coding: utf-8 -*-
'''
phixlib.generators
~~~~~~~~~~~~~~~~~~

This module provides value generators for initializing FIX fields with
valid values according to their specification and type. Methods defined
in this module automatically are attached as a classmethod to a Field.

'''
from functools import wraps
from pkg_resources import resource_string
from random import SystemRandom
import datetime
import json
import os
import string


random = SystemRandom()

ISO_CODES = json.loads(resource_string(__name__, 'spec/isocodes.json'))
GENERATORS = {}


try:
    with open('/usr/share/dict/words', 'rb') as wordlist:
        WORDLIST = wordlist.read().strip().splitlines()
except IOError:
    WORDLIST = None


def use_defaults(f):
    '''
    The purpose of this decorator is to wrap generator functions so a
    value is generated in the following order:

      1. If *use_defaults* is specified as a kwargs, Lookup the tag name
         in a dictionary of valid values for that tag and return one from
         the list if it exists.

      2. Choose a value from a tag's set of enums, if enums are defined
         for that particular tag.

      3. Generate a value for the current tag if other conditions are not met.
    '''

    @wraps(f)
    def wrapper(tag, **kwargs):
        using_defaults = kwargs.get('use_defaults', False)
        default_values = kwargs.get('default_values', {})

        if tag.name in default_values and using_defaults:
            return random.choice(default_values[tag.name])

        if tag.enums:
            return random.choice(tag.enums.keys())

        return f(tag, **kwargs)

    return wrapper


@use_defaults
def generate_AMT(tag, **kwargs):
    # this requires knowing the Quantity * Price
    pass


@use_defaults
def generate_BOOLEAN(tag, **kwargs):
    return random.choice('YN')


@use_defaults
def generate_CHAR(tag, **kwargs):
    return random.choice(string.punctuation.strip())


@use_defaults
def generate_COUNTRY(tag, **kwargs):
    return random.choice(ISO_CODES['countries'])


@use_defaults
def generate_CURRENCY(tag, **kwargs):
    return random.choice(ISO_CODES['currencies'])


@use_defaults
def generate_DATA(tag, **kwargs):
    return os.urandom(generate_LENGTH(tag, **kwargs))


@use_defaults
def generate_DAYOFMONTH(tag, **kwargs):
    return random.randint(0, 31)


@use_defaults
def generate_EXCHANGE(tag, **kwargs):
    return random.choice(ISO_CODES['exchanges'])


@use_defaults
def generate_FLOAT(tag, **kwargs):
    precision = kwargs.get('precision', 2)
    return float("{0}{1:.{2}f}".format(
        random.choice(['-', '']), random.random() * 100, precision))


@use_defaults
def generate_INT(tag, **kwargs):
    return random.randint(0, 5000)


@use_defaults
def generate_LANGUAGE(tag, **kwargs):
    return random.choice(ISO_CODES['languages'])


@use_defaults
def generate_LENGTH(tag, **kwargs):
    return int(kwargs.get('generate_LENGTH', random.randrange(256)))


@use_defaults
def generate_LOCALMKTDATE(tag, **kwargs):
    return datetime.datetime.now().strftime("%Y%m%d")


@use_defaults
def generate_MONTHYEAR(tag, **kwargs):
    yyyymm = "{0:04d}{1:02d}".format(random.randint(2009, 2019), random.randint(1, 12))
    yyyymmdd = "{0:04d}{1:02d}{2:02d}".format(random.randint(2009, 2019), random.randint(1, 12), random.randint(1, 31))
    yyyymmww = "{0:04d}{1:02d}{2:02d}".format(random.randint(2009, 2019), random.randint(1, 12), random.randint(1, 5))
    return random.choice([yyyymm, yyyymmdd, yyyymmww])


@use_defaults
def generate_MULTIPLECHARVALUE(tag, **kwargs):
    return ' '.join([generate_CHAR(tag, **kwargs) for i in xrange(kwargs.get('size', 5))])


@use_defaults
def generate_MULTIPLESTRINGVALUE(tag, **kwargs):
    pass


@use_defaults
def generate_NUMINGROUP(tag, **kwargs):
    pass


@use_defaults
def generate_PERCENTAGE(tag, **kwargs):
    return "{0:.{1}%}".format(random.random(), kwargs.get('precision', 2))


@use_defaults
def generate_PRICE(tag, **kwargs):
    return abs(generate_FLOAT(tag, **kwargs))


@use_defaults
def generate_PRICEOFFSET(tag, **kwargs):
    return generate_PRICE(tag, **kwargs)


@use_defaults
def generate_QTY(tag, **kwargs):
    return "%.4f" % (random.random() * 100, )


@use_defaults
def generate_SEQNUM(tag, **kwargs):
    pass


@use_defaults
def generate_STRING(tag, **kwargs):
    try:
        return random.choice(WORDLIST)
    except TypeError:
        alnums = string.letters + string.digits
        s = ''.join([random.choice(alnums) for x in
                     xrange(kwargs.get('size', 20))])
        return s


@use_defaults
def generate_TZTIMEONLY(tag, **kwargs):
    return datetime.datetime.utcnow().strftime("%H:%M:%SZ")


@use_defaults
def generate_TZTIMESTAMP(tag, **kwargs):
    return datetime.datetime.utcnow().strftime("%Y%m%d-%H:%M:%SZ")


@use_defaults
def generate_UTCDATEONLY(tag, **kwargs):
    return datetime.datetime.utcnow().strftime("%Y%m%d")


@use_defaults
def generate_UTCTIMEONLY(tag, **kwargs):
    return datetime.datetime.utcnow().strftime("%H:%M:%S.%f")[:-3]


@use_defaults
def generate_UTCTIMESTAMP(tag, **kwargs):
    return datetime.datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f")[:-3]


@use_defaults
def generate_XMLDATA(tag, **kwargs):
    pass


@use_defaults
def generate_BeginString(tag, **kwargs):
    if hasattr(tag, 'version'):
        return tag.version
    else:
        return 'FIX.%s' % (random.choice(['4.0', '4.1', '4.2', '4.3', '4.4', '5.0']))


@use_defaults
def generate_Symbol(tag, **kwargs):
    return ''.join([random.choice(string.uppercase) for _ in xrange(random.randrange(1,5))])


@use_defaults
def generate_TotQuoteEntries(tag, **kwargs):
    return 1


GENERATORS = {
 'AMT': generate_AMT,
 'BOOLEAN': generate_BOOLEAN,
 'CHAR': generate_CHAR,
 'COUNTRY': generate_COUNTRY,
 'CURRENCY': generate_CURRENCY,
 'DATA': generate_DATA,
 'DAYOFMONTH': generate_DAYOFMONTH,
 'EXCHANGE': generate_EXCHANGE,
 'FLOAT': generate_FLOAT,
 'INT': generate_INT,
 'LANGUAGE': generate_LANGUAGE,
 'LENGTH': generate_LENGTH,
 'LOCALMKTDATE': generate_LOCALMKTDATE,
 'MONTHYEAR': generate_MONTHYEAR,
 'MULTIPLECHARVALUE': generate_MULTIPLECHARVALUE,
 'MULTIPLEVALUECHAR': generate_MULTIPLECHARVALUE,
 'MULTIPLEVALUESTRING': generate_MULTIPLESTRINGVALUE,
 'MULTIPLESTRINGVALUE': generate_MULTIPLESTRINGVALUE,
 'NUMINGROUP': generate_NUMINGROUP,
 'PERCENTAGE': generate_PERCENTAGE,
 'PRICE': generate_PRICE,
 'PRICEOFFSET': generate_PRICEOFFSET,
 'QTY': generate_QTY,
 'SEQNUM': generate_SEQNUM,
 'STRING': generate_STRING,
 'TZTIMEONLY': generate_TZTIMEONLY,
 'TZTIMESTAMP': generate_TZTIMESTAMP,
 'UTCDATEONLY': generate_UTCDATEONLY,
 'UTCTIMEONLY': generate_UTCTIMEONLY,
 'UTCTIMESTAMP': generate_UTCTIMESTAMP,
 'XMLDATA': generate_XMLDATA
}

GENERATORS['BeginString'] = generate_BeginString
GENERATORS['Symbol'] = generate_Symbol
GENERATORS['TotQuoteEntries'] = generate_TotQuoteEntries
