# -*- coding: utf-8 -*-
'''
phixlib
~~~~~~~

Example API usage:

    >>> from phixlib import FIX

    >>> FIX.FIX42.BeginString()
    8=FIX.4.2|

    >>> FIX.FIX44.BeginString()
    8=FIX.4.4|

    >>> m = FIX.FIX42.NewOrderSingle()
    >>> m
    8=FIX.4.2|9=5|35=D|10=181|

    >>> m.initialize(ClOrdID='C1111')
    >>> m
    8=FIX.4.2|9=87|35=D|52=20150406-18:23:24.381|11=C1111|21=1|55=ESNZ|54=6|60=20150406-18:23:24.382|40=5|10=176|

    >>> order = FIX.FIX42.NewOrderSingle.fromstring(str(m))
    >>> order
    8=FIX.4.2|9=87|35=D|52=20150406-18:23:24.381|11=C1111|21=1|55=ESNZ|54=6|60=20150406-18:23:24.382|40=5|10=176|

Initializing fields at construction, or from an existing message:

    >>> order = FIX.FIXMessage.fromstring('8=FIX.4.2|...')
    >>> order = FIX.FIXMessage(BeginString='FIX.4.2', MsgType='D', ClOrdID='C1111', **kwargs)
    >>>
    >>> order = FIX.FIX42.NewOrderSingle.fromstring('8=FIX.4.2|...')
    >>> order = FIX.FIX42.NewOrderSingle(ClOrdID='C1111', **kwargs)

Getting and setting fields in the message:

    >>> order.header.get(FIX.FIX42.MsgSeqNum)
    >>> order.header.set(FIX.FIX42.MsgSeqNum(2))
    34=2|
    >>>
    >>> order.get(11)
    11=C1111|
    >>> order.get('11')
    11=C1111|
    >>> order.get('ClOrdID')
    11=C1111|
    >>> order.get(FIX.FIX42.NewOrderSingle.ClOrdID)
    11=C1111|
    >>> order.get(FIX.FIX42.ClOrdID)
    11=C1111|
    >>>
    >>> order.set(FIX.FIX42.NewOrderSingle.ClOrdID('C12345'))
    11=C12345|
    >>> order.set(FIX.FIX42.ClOrdID('C12345'))
    11=C12345|
    >>> order.set(11, 'C12345')
    11=C12345|
    >>> order.set('11', 'C12345')
    11=C12345|
    >>> order.set('ClOrdID', 'C12345')
    11=C12345|

'''
from pkg_resources import resource_string
from .fix import FIX, Field, Group


__all__ = ['FIX']


FIX.register_version(resource_string(__name__, 'spec/FIX42.xml'))
FIX.register_version(resource_string(__name__, 'spec/FIX43.xml'))
FIX.register_version(resource_string(__name__, 'spec/FIX44.xml'))
