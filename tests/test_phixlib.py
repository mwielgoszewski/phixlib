# -*- coding: utf-8 -*-
from pprint import pprint

from phixlib import FIX
from phixlib.fix import Field, FIXMessage, Group
from phixlib.parser import parse_message


def test_registry():

    assert FIX.FIXMessage
    assert FIX.FIXMessage.Header
    assert FIX.FIXMessage.Trailer
    assert not FIX.FIXMessage.msgcat
    assert not FIX.FIXMessage.msgtype
    assert not FIX.FIXMessage.name
    assert not FIX.FIXMessage._all

    for version in FIX._versions:
        assert FIX[version].FIXMessage, "%s does not have a FIXMessage registered" % (version, )
        assert FIX[version].FIXMessage.Header
        assert FIX[version].FIXMessage.Trailer
        assert not FIX[version].FIXMessage.msgcat
        assert not FIX[version].FIXMessage.msgtype
        assert not FIX[version].FIXMessage.name
        assert not FIX[version].FIXMessage._all
        assert issubclass(FIX[version].FIXMessage, FIX.FIXMessage)

    assert 'FIX42' in FIX
    assert 'FIX.4.2' in FIX
    assert 'NewOrderSingle' in FIX.FIX42
    assert 'NewOrderSingle' in FIX['FIX.4.2']
    assert FIX.FIX42.NewOrderSingle
    assert FIX.FIX42.Messages.NewOrderSingle

    assert FIX.FIX42.NewOrderSingle.msgtype == 'D'
    assert FIX.FIX42.Messages.NewOrderSingle.msgtype == 'D'
    assert FIX.FIX42.NewOrderSingle.name == 'NewOrderSingle'
    assert FIX.FIX42.Messages.NewOrderSingle.name == 'NewOrderSingle'

    assert FIX.FIX42.OrdType.number == '40'
    assert FIX.FIX42.OrdType.name == 'OrdType'
    assert FIX.FIX42.OrdType.type == 'CHAR'
    assert FIX.FIX42.OrdType.MARKET == '1'
    assert FIX.FIX42.OrdType.enums['1'] == 'MARKET'
    assert '1' in FIX.FIX42.OrdType.enums

    assert FIX.FIX42.NewOrderSingle.OrdType
    assert FIX.FIX42.NewOrderSingle.OrdType.MARKET == FIX.FIX42.OrdType.MARKET

    assert issubclass(FIX.FIX42.MassQuote, FIXMessage)
    assert issubclass(FIX.FIX42.MassQuote.NoQuoteSets, Group)
    assert issubclass(FIX.FIX42.MassQuote.NoQuoteSets, FIX.FIX42.NoQuoteSets)
    assert issubclass(FIX.FIX42.MassQuote.NoQuoteSets.NoQuoteEntries, Group)
    assert issubclass(FIX.FIX42.MassQuote.NoQuoteSets.NoQuoteEntries.QuoteEntryID, Field)

    assert issubclass(FIX.FIX42.NoQuoteSets, Field)
    assert not issubclass(FIX.FIX42.NoQuoteSets, Group)

    assert id(FIX.FIX42.OrdType.enums) == id(FIX.FIX42.NewOrderSingle.OrdType.enums)
    assert id(FIX.FIX42.OrdType.enums) == id(FIX.FIX42.MassQuote.NoQuoteSets.NoQuoteEntries.OrdType.enums)

    assert FIX.get_field_number(FIX.FIX42.OrdType.name) == FIX.FIX42.OrdType.number
    assert not FIX.get_field_number(-1)

    assert FIX.get_field_name(FIX.FIX42.OrdType.number) == FIX.FIX42.OrdType.name
    assert not FIX.get_field_name(-1)

    assert FIX.get_message_name(FIX.FIX42.NewOrderSingle.msgtype) == FIX.FIX42.NewOrderSingle.name
    assert not FIX.get_message_name('NotAMessage')

    assert FIX.get_message_type(FIX.FIX42.NewOrderSingle.name) == FIX.FIX42.NewOrderSingle.msgtype
    assert not FIX.get_message_type('_')

def test_str():
    assert str(FIX.FIX42.OrdType(1)) == '40=1\001'
    assert repr(FIX.FIX42.OrdType(1)) == '40=1|'
    assert str(FIX.FIX42.OrdType(FIX.FIX42.OrdType.MARKET)) == '40=1\001'
    assert repr(FIX.FIX42.OrdType(FIX.FIX42.OrdType.MARKET)) == '40=1|'

    group = [{'AllocAccount': 'Marcin', 'AllocShares': 10}]
    group2 = group * 2
    group3 = group2[:]
    group3[-1].pop('AllocShares')
    group3.append({'AllocAccount': 'Jay', 'AllocShares': 5})

    # Verify NoAllocs=1
    order1 = FIX.FIX42.NewOrderSingle.NoAllocs(*group)
    assert len(order1) == 1
    assert str(order1) == '78=1\001'
    assert repr(order1) == '78=1|'

    order2 = FIX.FIX42.NewOrderSingle.NoAllocs(*group2)
    # Verify NoAllocs=2
    assert len(order2) == 2
    assert str(order2) == '78=2\001'
    assert repr(order2) == '78=2|'

    order3 = FIX.FIX42.NewOrderSingle.NoAllocs(*group3)
    # Verify NoAllocs=3, even though the 2nd group only has a single tag
    assert len(order3) == 3
    assert str(order3) == '78=3\001'
    assert repr(order3) == '78=3|'

    NoQuoteSet = [
        {'NoQuoteEntries': [
            {'BidSize': '1000000',
             'BidSpotRate': '1.4363',
             'OfferSize': '900000',
             'OfferSpotRate': '1.4365',
             'QuoteEntryID': '0'},
            {'BidSize': '7000000',
             'BidSpotRate': '1.4363',
             'OfferSize': '800000',
             'OfferSpotRate': '1.4365',
             'QuoteEntryID': '1'},
            ],  
         'QuoteSetID': '123'},
        {'NoQuoteEntries': [
            {'BidSize': '1000000',
             'BidSpotRate': '1.4363',
             'OfferSize': '900000',
             'OfferSpotRate': '1.4365',
             'QuoteEntryID': '2'},
            {'BidSize': '7000000',
             'BidSpotRate': '1.4363',
             'OfferSize': '800000',
             'OfferSpotRate': '1.4365',
             'QuoteEntryID': '3'},
            ],  
         'QuoteSetID': '234'},
    ]

    noQuoteSet = FIX.FIX42.MassQuote.NoQuoteSets(*NoQuoteSet)

    # Verify NoQuoteSets=2
    assert len(noQuoteSet) == 2
    assert str(noQuoteSet) == '296=2\001'
    assert repr(noQuoteSet) == '296=2|'

    # Verify QuoteSetID=123
    assert str(noQuoteSet[0][0]) == '302=123\001'
    assert repr(noQuoteSet[0][0]) == '302=123|'

    # Verify NoQuoteEntries=2
    assert len(noQuoteSet[0][1]) == 2
    assert str(noQuoteSet[0][1]) == '295=2\001'
    assert repr(noQuoteSet[0][1]) == '295=2|'

    # Verify QuoteSetID=234
    assert str(noQuoteSet[1][0]) == '302=234\001'
    assert repr(noQuoteSet[1][0]) == '302=234|'

    # Verify NoQuoteEntries=2
    assert len(noQuoteSet[1][1]) == 2
    assert str(noQuoteSet[1][1]) == '295=2\001'
    assert repr(noQuoteSet[1][1]) == '295=2|'

    assert noQuoteSet[0][0].group is noQuoteSet
    assert noQuoteSet[0][1].group is noQuoteSet

    assert noQuoteSet[0][1][0][0].group is noQuoteSet[0][1]
    assert noQuoteSet[0][1][1][0].group is noQuoteSet[0][1]

    NoQuoteSet[0]['NotARealField'] = 'TEST'   # this field should not get initialized in the group

    message = FIX.FIX42.MassQuote(NoQuoteSets=NoQuoteSet)
    assert 'TEST' not in str(message)


def test_parser():
    expected = {
         'BeginString': 'FIX.4.2',
         'BodyLength': '295',
         'CheckSum': '215',
         'MsgSeqNum': '2',
         'MsgType': 'i',
         'NoQuoteSets': [{'NoQuoteEntries': [{'BidSize': '1000000',
                                              'BidSpotRate': '1.4363',
                                              'OfferSize': '900000',
                                              'OfferSpotRate': '1.4365',
                                              'QuoteEntryID': '0'},
                                             {'BidSize': '7000000',
                                              'BidSpotRate': '1.4363',
                                              'OfferSize': '800000',
                                              'OfferSpotRate': '1.4365',
                                              'QuoteEntryID': '1'}],
                          'QuoteSetID': '123'},
                         {'NoQuoteEntries': [{'BidSize': '1000000',
                                              'BidSpotRate': '1.4363',
                                              'OfferSize': '900000',
                                              'OfferSpotRate': '1.4365',
                                              'QuoteEntryID': '2'},
                                             {'BidSize': '7000000',
                                              'BidSpotRate': '1.4363',
                                              'OfferSize': '800000',
                                              'OfferSpotRate': '1.4365',
                                              'QuoteEntryID': '3'}],
                          'QuoteSetID': '234'}],
         'QuoteID': '1',
         'SenderCompID': 'PXMD',
         'SendingTime': '20140922-14:48:49.825',
         'TargetCompID': 'Q037'}

    formatted = '''8=FIX.4.2|9=295|35=i|49=PXMD|56=Q037|34=2|52=20140922-14:48:49.825|117=1|296=2|302=123|295=2|299=0|134=1000000|135=900000|188=1.4363|190=1.4365|299=1|134=7000000|135=800000|188=1.4363|190=1.4365|302=234|295=2|299=2|134=1000000|135=900000|188=1.4363|190=1.4365|299=3|134=7000000|135=800000|188=1.4363|190=1.4365|10=215|'''
    assert parse_message(formatted) == expected, pprint(parse_message(formatted))

    message = FIX.FIX42.MassQuote(**expected)
    assert repr(message) == formatted

    message = FIX.FIXMessage(**expected)
    assert repr(message) == formatted

    fromstring = FIX.FIX42.MassQuote.fromstring(formatted)
    assert repr(fromstring) == formatted

    fromstring = FIX.FIXMessage.fromstring(formatted)
    assert repr(fromstring) == formatted

    # since this is going to mess up the CheckSum and change the MsgType
    # field as rendered in the formatted string, let's account for that

    fromstring = FIX.FIX42.MassQuote.fromstring(formatted, MsgType='A')
    assert repr(fromstring)[:-4] == formatted.replace('35=i', '35=A')[:-4]
    assert isinstance(fromstring, FIX.FIX42.MassQuote)
    assert not isinstance(fromstring, FIX.FIX42.Logon)

    fromstring = FIX.FIXMessage.fromstring(formatted, MsgType='A')
    #assert repr(fromstring)[:-4] == formatted.replace('35=i', '35=A')[:-4]
    assert isinstance(fromstring, FIX.FIX42.Logon)

    expected = {
         'BeginString': 'FIX.4.2',
         'BodyLength': '156',
         'CheckSum': '228',
         'MsgSeqNum': '2',
         'MsgType': 'J',
         'NoAllocs': [{'AllocAccount': 'Marcin',
                       'AllocShares': '10',
                       'NoMiscFees': [{'MiscFeeAmt': '7.99'}]},
                      {'AllocAccount': 'Jason', 'AllocShares': '5'}],
         'NoOrders': [{'ClOrdID': 'C11111', 'OrderID': 'O11111'},
                      {'ClOrdID': 'C22222', 'OrderID': 'O22222'},
                      {'OrderID': 'O33333'}],
         'SenderCompID': 'PXMD',
         'SendingTime': '20140922-14:48:49.825',
         'TargetCompID': 'Q037'}

    formatted = '''8=FIX.4.2|9=156|35=J|49=PXMD|56=Q037|34=2|52=20140922-14:48:49.825|73=3|11=C11111|37=O11111|11=C22222|37=O22222|37=O33333|78=2|79=Marcin|80=10|136=1|137=7.99|79=Jason|80=5|10=228|'''
    assert parse_message(formatted) == expected, pprint(parse_message(formatted))

    message = FIX.FIX42.Allocation(**expected)
    assert repr(message) == formatted

    message = FIX.FIXMessage(**expected)
    assert repr(message) == formatted

    fromstring = FIX.FIX42.Allocation.fromstring(formatted)
    assert repr(fromstring) == formatted

    fromstring = FIX.FIXMessage.fromstring(formatted)
    assert repr(fromstring) == formatted

    expected = {
         'BeginString': 'FIX.4.2',
         'BodyLength': '182',
         'CheckSum': '005',
         'MsgSeqNum': '2',
         'MsgType': 'J',
         'NoAllocs': [{'AllocAccount': 'Marcin',
                       'AllocShares': '10',
                       'NoMiscFees': [{'MiscFeeAmt': '7.99'}]},
                      {'AllocAccount': 'Jason', 'AllocShares': '5'},
                      {'AllocShares': '10'},
                      {'AllocAccount': 'Tester'},
                      ],
         'NoOrders': [{'ClOrdID': 'C11111', 'OrderID': 'O11111'},
                      {'ClOrdID': 'C22222', 'OrderID': 'O22222'},
                      {'OrderID': 'O33333'},
                      {'ClOrdID': 'O44444'}],
         'SenderCompID': 'PXMD',
         'SendingTime': '20140922-14:48:49.825',
         'TargetCompID': 'Q037'}

    formatted = '8=FIX.4.2|9=182|35=J|49=PXMD|56=Q037|34=2|52=20140922-14:48:49.825|73=4|11=C11111|37=O11111|11=C22222|37=O22222|37=O33333|11=O44444|78=4|79=Marcin|80=10|136=1|137=7.99|79=Jason|80=5|80=10|79=Tester|10=005|'
    assert parse_message(formatted) == expected, pprint(parse_message(formatted))

    message = FIX.FIX42.Allocation(**expected)
    assert repr(message) == formatted

    message = FIX.FIXMessage(**expected)
    assert repr(message) == formatted

    fromstring = FIX.FIX42.Allocation.fromstring(formatted)
    assert repr(fromstring) == formatted

    fromstring = FIX.FIXMessage.fromstring(formatted)
    assert repr(fromstring) == formatted

    #FIX.register_version('phixlib/spec/FIX50SP2.xml')
    #fromstring = FIX.FIX50.AllocationInstruction.fromstring(formatted, BeginString='FIX.5.0')
    #assert repr(fromstring)[9:-7] == formatted[9:-7]
    #print repr(fromstring)

    '''
    expected = {
         'BeginString': 'FIX.4.2',
         'BodyLength': '197',
         'CheckSum': '225',
         'MsgSeqNum': '2',
         'MsgType': 'BBBBBBBBBBBBBBBB',
         'NoAllocs': [{'AllocAccount': 'Marcin',
                       'AllocShares': '10',
                       'NoMiscFees': [{'MiscFeeAmt': '7.99'}]},
                      {'AllocAccount': 'Jason', 'AllocShares': '5'},
                      {'AllocShares': '10'},
                      {'AllocAccount': 'Tester'},
                      ],
         'NoOrders': [{'ClOrdID': 'C11111', 'OrderID': 'O11111'},
                      {'ClOrdID': 'C22222', 'OrderID': 'O22222'},
                      {'OrderID': 'O33333'},
                      {'ClOrdID': 'O44444'}],
         'SenderCompID': 'PXMD',
         'SendingTime': '20140922-14:48:49.825',
         'TargetCompID': 'Q037'}

    message.header._initialized['MsgType'].value = 'BBBBBBBBBBBBBBBB'
    formatted = '8=FIX.4.2|9=197|35=BBBBBBBBBBBBBBBB|49=PXMD|56=Q037|34=2|52=20140922-14:48:49.825|73=4|11=C11111|37=O11111|11=C22222|37=O22222|37=O33333|11=O44444|78=4|79=Marcin|80=10|136=1|137=7.99|79=Jason|80=5|80=10|79=Tester|10=225|'
    assert parse_message(formatted) == expected, pprint(parse_message(formatted))
    '''

    expected = {
        'BeginString': 'FIX.4.2',
        'BodyLength': '74',
        'CheckSum': '213',
        'EncryptMethod': '1',
        'HeartBtInt': '3503',
        'MsgType': 'A',
        'RawData': 'AAAAAAAAAAAAAAAA\001AAA',
        'RawDataLength': '20',
        'SendingTime': '20150407-04:12:54.885'}


    formatted = '8=FIX.4.2\0019=74\00135=A\00152=20150407-04:12:54.885\00198=1\001108=3503\00195=20\00196=AAAAAAAAAAAAAAAA\001AAA\00110=213\001'
    assert parse_message(formatted) == expected, pprint(parse_message(formatted))

    fromstring = FIX.FIX42.Logon.fromstring(formatted)
    assert str(fromstring) == formatted


def test_getfield():
    expected = {
         'BeginString': 'FIX.4.2',
         'BodyLength': '182',
         'CheckSum': '005',
         'MsgSeqNum': '2',
         'MsgType': 'J',
         'NoAllocs': [{'AllocAccount': 'Marcin',
                       'AllocShares': '10',
                       'NoMiscFees': [{'MiscFeeAmt': '7.99'}]},
                      {'AllocAccount': 'Jason', 'AllocShares': '5'},
                      {'AllocShares': '10'},
                      {'AllocAccount': 'Tester'},
                      ],
         'NoOrders': [{'ClOrdID': 'C11111', 'OrderID': 'O11111'},
                      {'ClOrdID': 'C22222', 'OrderID': 'O22222'},
                      {'OrderID': 'O33333'},
                      {'ClOrdID': 'O44444'}],
         'SenderCompID': 'PXMD',
         'SendingTime': '20140922-14:48:49.825',
         'TargetCompID': 'Q037'}

    formatted = '8=FIX.4.2|9=182|35=J|49=PXMD|56=Q037|34=2|52=20140922-14:48:49.825|73=4|11=C11111|37=O11111|11=C22222|37=O22222|37=O33333|11=O44444|78=4|79=Marcin|80=10|136=1|137=7.99|79=Jason|80=5|80=10|79=Tester|10=005|'
    message = FIX.FIX42.Allocation(**expected)

    assert str(message.header.get(FIX.FIX42.BeginString)) == '8=FIX.4.2\001'
    assert str(message.header.get(FIX.FIX42.BeginString())) == '8=FIX.4.2\001'
    assert str(message.header.get(FIX.FIX42.BeginString.name)) == '8=FIX.4.2\001'
    assert str(message.header.get(FIX.FIX42.BeginString.number)) == '8=FIX.4.2\001'
    assert not message.header.get(object())

    assert str(message.trailer.get(FIX.FIX42.CheckSum)) == '10=005\001'
    assert str(message.trailer.get(FIX.FIX42.CheckSum())) == '10=005\001'
    assert str(message.trailer.get(FIX.FIX42.CheckSum.name)) == '10=005\001'
    assert str(message.trailer.get(FIX.FIX42.CheckSum.number)) == '10=005\001'
    assert not message.trailer.get(object())

    assert len(message.get(FIX.FIX42.Allocation.NoAllocs)) == 4
    assert len(message.get(FIX.FIX42.Allocation.NoAllocs())) == 4
    assert len(message.get(FIX.FIX42.Allocation.NoAllocs.name)) == 4
    assert len(message.get(FIX.FIX42.Allocation.NoAllocs.number)) == 4
    assert len(message.get(FIX.FIX42.NoAllocs)) == 4
    assert len(message.get(FIX.FIX42.NoAllocs())) == 4
    assert len(message.get(FIX.FIX42.NoAllocs.name)) == 4
    assert len(message.get(FIX.FIX42.NoAllocs.number)) == 4
    assert len(message.get('NoAllocs')) == 4
    assert len(message.get('78')) == 4
    assert len(message.get(78)) == 4

    # Group objects support slice notation, use [:] to copy as list
    # versus calling list(), which will flatten the Group

    assert len(message.get('NoAllocs')[:]) == 4

    assert str(message.get(FIX.FIX42.Allocation.NoAllocs)) == '78=4\001'
    assert str(message.get(FIX.FIX42.Allocation.NoAllocs.name)) == '78=4\001'
    assert str(message.get(FIX.FIX42.Allocation.NoAllocs.number)) == '78=4\001'
    assert str(message.get(FIX.FIX42.NoAllocs)) == '78=4\001'
    assert str(message.get(FIX.FIX42.NoAllocs())) == '78=4\001'
    assert str(message.get(FIX.FIX42.NoAllocs.name)) == '78=4\001'
    assert str(message.get(FIX.FIX42.NoAllocs.number)) == '78=4\001'
    assert str(message.get('NoAllocs')) == '78=4\001'
    assert str(message.get('78')) == '78=4\001'
    assert str(message.get(78)) == '78=4\001'

    assert message.get(0) is None
    assert message.get('0') is None
    assert message.get('XXXXXX') is None
    assert message.get(object()) is None


def test_setfield():

    args = ('C111111', )

    for setter in (int(FIX.FIX42.NewOrderSingle.ClOrdID.number),
                   FIX.FIX42.NewOrderSingle.ClOrdID.number,
                   FIX.FIX42.NewOrderSingle.ClOrdID.name,
                   FIX.FIX42.NewOrderSingle.ClOrdID):

        order = FIX.FIX42.NewOrderSingle()
        field = order.set(setter, *args)

        assert field is not None
        assert field.name == FIX.FIX42.NewOrderSingle.ClOrdID.name
        assert field.number == FIX.FIX42.NewOrderSingle.ClOrdID.number
        assert field.value == args[0]
        assert field.name in order._initialized
        assert id(field) == id(order._initialized[field.name])
        assert order._initialized[field.name].value == args[0]

        assert str(field) in str(order)
        assert repr(field) in repr(order)

    field = order.set(FIX.FIX42.ClOrdID.number, *args)
    assert str(field) in str(order)
    assert repr(field) in repr(order)

    field = None
    order = None

    order = FIX.FIX42.NewOrderSingle()
    field_ = FIX.FIX42.NewOrderSingle.ClOrdID(*args)
    field = order.set(field_)

    assert field is field_

    assert field is not None
    assert field.name == FIX.FIX42.NewOrderSingle.ClOrdID.name
    assert field.number == FIX.FIX42.NewOrderSingle.ClOrdID.number
    assert field.value == args[0]
    assert field.name in order._initialized
    assert id(field) == id(order._initialized['ClOrdID'])
    assert order._initialized['ClOrdID'].value == args[0]

    assert str(field) in str(order)
    assert repr(field) in repr(order)

    field = None
    order = None

    order = FIX.FIX42.NewOrderSingle()
    field_ = FIX.FIX42.ClOrdID(*args)
    field = order.set(field_)

    assert field is field_

    assert field is not None
    assert field.name == FIX.FIX42.NewOrderSingle.ClOrdID.name
    assert field.number == FIX.FIX42.NewOrderSingle.ClOrdID.number
    assert field.value == args[0]
    assert field.name in order._initialized
    assert id(field) == id(order._initialized['ClOrdID'])
    assert order._initialized['ClOrdID'].value == args[0]

    assert str(field) in str(order)
    assert repr(field) in repr(order)

    # test where the field we want to set is not part of the message.

    order = FIX.FIX42.NewOrderSingle()
    field_ = FIX.FIX42.TestReqID(*args)
    field = order.set(field_)

    assert field is field_
    assert field_.name in order._initialized
    assert str(field_) in str(order)
    assert repr(field_) in repr(order)

    order = FIX.FIX42.NewOrderSingle()
    field = order.set(FIX.FIX42.TestReqID, *args)

    assert field is None
    assert field_.name not in order._initialized
    assert str(field_) not in str(order)
    assert repr(field_) not in repr(order)

    order = FIX.FIX42.NewOrderSingle()
    field = order.set(FIX.FIX42.TestReqID.name, *args)

    assert field is None
    assert field_.name not in order._initialized
    assert str(field_) not in str(order)
    assert repr(field_) not in repr(order)

    order = FIX.FIX42.NewOrderSingle()
    field = order.set(FIX.FIX42.TestReqID.number, *args)

    assert field is None
    assert field_.name not in order._initialized
    assert str(field_) not in str(order)
    assert repr(field_) not in repr(order)

    order = FIX.FIX42.NewOrderSingle()
    field = order.set(int(FIX.FIX42.TestReqID.number), *args)

    assert field is None
    assert field_.name not in order._initialized
    assert str(field_) not in str(order)
    assert repr(field_) not in repr(order)

    order = FIX.FIX42.NewOrderSingle()
    field = order.set(FIX.FIX42.TestReqID, *args, ignore_spec=True)

    assert field is not None
    assert field.name in order._initialized
    assert str(field) in str(order)
    assert repr(field) in repr(order)

    order = FIX.FIX42.NewOrderSingle()
    field = order.set(FIX.FIX42.TestReqID.name, *args, ignore_spec=True)

    assert field is not None
    assert field.name in order._initialized
    assert str(field) in str(order)
    assert repr(field) in repr(order)

    order = FIX.FIX42.NewOrderSingle()
    field = order.set(FIX.FIX42.TestReqID.number, *args, ignore_spec=True)

    assert field is not None
    assert field.name in order._initialized
    assert str(field) in str(order)
    assert repr(field) in repr(order)

    order = FIX.FIX42.NewOrderSingle()
    field = order.set(int(FIX.FIX42.TestReqID.number), *args, ignore_spec=True)

    assert field is not None
    assert field.name in order._initialized
    assert str(field) in str(order)
    assert repr(field) in repr(order)

    # test __setitem__ and __delitem__ for Group
    expected = {
         'BeginString': 'FIX.4.2',
         'BodyLength': '182',
         'CheckSum': '005',
         'MsgSeqNum': '2',
         'MsgType': 'J',
         'NoAllocs': [{'AllocAccount': 'Marcin',
                       'AllocShares': '10',
                       'NoMiscFees': [{'MiscFeeAmt': '7.99'}]},
                      {'AllocAccount': 'Jason', 'AllocShares': '5'},
                      {'AllocShares': '10'},
                      {'AllocAccount': 'Tester'},
                      ],
         'NoOrders': [{'ClOrdID': 'C11111', 'OrderID': 'O11111'},
                      {'ClOrdID': 'C22222', 'OrderID': 'O22222'},
                      {'OrderID': 'O33333'},
                      {'ClOrdID': 'O44444'}],
         'SenderCompID': 'PXMD',
         'SendingTime': '20140922-14:48:49.825',
         'TargetCompID': 'Q037'}
    formatted = '8=FIX.4.2|9=182|35=J|49=PXMD|56=Q037|34=2|52=20140922-14:48:49.825|73=4|11=C11111|37=O11111|11=C22222|37=O22222|37=O33333|11=O44444|78=4|79=Marcin|80=10|136=1|137=7.99|79=Jason|80=5|80=10|79=Tester|10=005|'
    message = FIX.FIX42.Allocation.fromstring(formatted)

    field = message.get(FIX.FIX42.Allocation.NoAllocs)
    alloc = field[-1]   #{'AllocAccount': 'Tester'}
    del field[-1]   # alloc

    assert str(field) == '78=3\001'
    assert len(field) == 3

    assert repr(message)[:-4].endswith('78=3|79=Marcin|80=10|136=1|137=7.99|79=Jason|80=5|80=10|10=')

    field[-1] = alloc
    assert str(field) == '78=3\001'
    assert len(field) == 3

    assert str(message)
    assert repr(message)[:-4].endswith('78=3|79=Marcin|80=10|136=1|137=7.99|79=Jason|80=5|79=Tester|10=')

    assert alloc in field

    # test header

    for setter in (int(FIX.FIX42.NewOrderSingle.Header.OnBehalfOfCompID.number),
                   FIX.FIX42.NewOrderSingle.Header.OnBehalfOfCompID.number,
                   FIX.FIX42.NewOrderSingle.Header.OnBehalfOfCompID.name,
                   FIX.FIX42.NewOrderSingle.Header.OnBehalfOfCompID):

        order = FIX.FIX42.NewOrderSingle()
        field = order.header.set(setter, 'TEST')

        assert field is not None
        assert field.name == FIX.FIX42.NewOrderSingle.Header.OnBehalfOfCompID.name
        assert field.number == FIX.FIX42.NewOrderSingle.Header.OnBehalfOfCompID.number
        assert field.value == 'TEST'
        assert field.name in order.header._initialized
        assert id(field) == id(order.header._initialized[field.name])
        assert order.header._initialized[field.name].value == 'TEST'

        assert str(field) in str(order)
        assert repr(field) in repr(order)

    for setter in (int(FIX.FIX42.NewOrderSingle.Trailer.Signature.number),
                   FIX.FIX42.NewOrderSingle.Trailer.Signature.number,
                   FIX.FIX42.NewOrderSingle.Trailer.Signature.name,
                   FIX.FIX42.NewOrderSingle.Trailer.Signature):

        order = FIX.FIX42.NewOrderSingle()
        field = order.trailer.set(setter, 'TEST')

        assert field is not None
        assert field.name == FIX.FIX42.NewOrderSingle.Trailer.Signature.name
        assert field.number == FIX.FIX42.NewOrderSingle.Trailer.Signature.number
        assert field.value == 'TEST'
        assert field.name in order.trailer._initialized
        assert id(field) == id(order.trailer._initialized[field.name])
        assert order.trailer._initialized[field.name].value == 'TEST'

        assert str(field) in str(order)
        assert repr(field) in repr(order)


def test_contains():

    args = ('C111111', )

    order = FIX.FIX42.NewOrderSingle()
    field = FIX.FIX42.NewOrderSingle.ClOrdID(*args)
    order.set(field)

    assert field in order
    assert field.name in order
    assert field.number in order
    assert field.__class__ in order
    assert int(field.number) in order

    order = FIX.FIX42.NewOrderSingle()
    field_ = FIX.FIX42.TestReqID(*args)
    field = order.set(FIX.FIX42.TestReqID, *args)

    assert field is None
    assert field_ not in order
    assert field_.name not in order
    assert field_.number not in order
    assert field_.__class__ not in order
    assert int(field_.number) not in order

    order = FIX.FIX42.NewOrderSingle()
    field_ = FIX.FIX42.TestReqID(*args)
    field = order.set(FIX.FIX42.TestReqID, *args, ignore_spec=True)

    assert field in order
    assert field_.name in order
    assert field_.number in order
    assert field_.__class__ in order
    assert int(field_.number) in order

    assert not object() in order


def test_equality():

    args1 = ('C111111', )
    args2 = ('C111112', )

    field = FIX.FIX42.NewOrderSingle.ClOrdID(*args1)
    other = FIX.FIX42.NewOrderSingle.ClOrdID(*args1)

    assert field == other
    assert field == field
    assert other == other

    field = FIX.FIX42.NewOrderSingle.ClOrdID(*args1)
    other = FIX.FIX42.NewOrderSingle.ClOrdID(*args2)

    assert field != other
    assert not field == other

    other = FIX.FIX42.BeginString()
    assert field != other
    assert not field == other

    other = FIX.FIX42.NewOrderSingle.ClOrdID(*args2)
    other.number = '0'
    assert field != other
    assert not field == other

    assert FIX.FIX42.NewOrderSingle.ClOrdID.number != '0'


def test_iadd_isub():

    args = ('C111111', )

    order = FIX.FIX42.NewOrderSingle()
    field = FIX.FIX42.NewOrderSingle.ClOrdID(*args)

    order += field

    assert field in order

    order -= field

    assert field not in order


def test_malformed():

    expected = {
         'BeginString': 'FIX.4.2',
         'BodyLength': '156',
         'CheckSum': '228',
         'MsgSeqNum': '2',
         'MsgType': 'J',
         'NoAllocs': [{'AllocAccount': 'Marcin',
                       'AllocShares': '10',
                       'NoMiscFees': [{'MiscFeeAmt': '7.99'}]},
                      {'AllocAccount': 'Jason', 'AllocShares': '5'}],
         'NoOrders': [{'ClOrdID': 'C11111', 'OrderID': 'O11111'},
                      {'ClOrdID': 'C22222', 'OrderID': 'O22222'},
                      {'OrderID': 'O33333'}],
         'SenderCompID': 'PXMD',
         'SendingTime': '20140922-14:48:49.825',
         'TargetCompID': 'Q037'}

    _expected = expected.copy()

    # this one is good

    formatted = '''8=FIX.4.2|9=156|35=J|49=PXMD|56=Q037|34=2|52=20140922-14:48:49.825|73=3|11=C11111|37=O11111|11=C22222|37=O22222|37=O33333|78=2|79=Marcin|80=10|136=1|137=7.99|79=Jason|80=5|10=228|'''
    assert parse_message(formatted) == expected, pprint(parse_message(formatted))

    # |||||

    formatted = '''8=FIX.4.2|9=156|35=J|49=PXMD|56=Q037|34=2|52=20140922-14:48:49.825|73=3|11=C11111|37=O11111|11=C22222|37=O22222|37=O33333|78=2|79=Marcin|80=10|136=1|137=7.99|||||79=Jason|80=5|10=228|'''
    assert parse_message(formatted) == expected, pprint(parse_message(formatted))

    # |a|a|a|a|

    formatted = '''8=FIX.4.2|9=156|35=J|49=PXMD|56=Q037|34=2|52=20140922-14:48:49.825|73=3|11=C11111|37=O11111|11=C22222|37=O22222|37=O33333|78=2|79=Marcin|80=10|136=1|137=7.99|a|a|a|a|79=Jason|80=5|10=228|'''
    assert parse_message(formatted) == expected, pprint(parse_message(formatted))

    # |=|

    formatted = '''8=FIX.4.2|9=156|35=J|49=PXMD|56=Q037|34=2|52=20140922-14:48:49.825|73=3|11=C11111|37=O11111|11=C22222|37=O22222|37=O33333|78=2|79=Marcin|80=10|136=1|137=7.99|=|79=Jason|80=5|10=228|'''
    assert parse_message(formatted) == expected, pprint(parse_message(formatted))

    # |==|=|

    formatted = '''8=FIX.4.2|9=156|35=J|49=PXMD|56=Q037|34=2|52=20140922-14:48:49.825|73=3|11=C11111|37=O11111|11=C22222|37=O22222|37=O33333|78=2|79=Marcin|80=10|136=1|137=7.99|==|=|79=Jason|80=5|10=228|'''
    assert parse_message(formatted) == expected, pprint(parse_message(formatted))

    # |22|=|

    formatted = '''8=FIX.4.2|9=156|35=J|49=PXMD|56=Q037|34=2|52=20140922-14:48:49.825|73=3|11=C11111|37=O11111|11=C22222|37=O22222|37=O33333|78=2|79=Marcin|80=10|136=1|137=7.99|22|=|79=Jason|80=5|10=228|'''
    assert parse_message(formatted) == expected, pprint(parse_message(formatted))

    # |=asdf|

    formatted = '''8=FIX.4.2|9=156|35=J|49=PXMD|56=Q037|34=2|52=20140922-14:48:49.825|73=3|11=C11111|37=O11111|11=C22222|37=O22222|37=O33333|78=2|79=Marcin|80=10|136=1|137=7.99|=asdf|79=Jason|80=5|10=228|'''
    assert parse_message(formatted) == expected, pprint(parse_message(formatted))

    # |A=A| (not a digit)

    formatted = '''8=FIX.4.2|9=156|35=J|49=PXMD|56=Q037|34=2|52=20140922-14:48:49.825|73=3|11=C11111|37=O11111|11=C22222|37=O22222|37=O33333|78=2|79=Marcin|80=10|136=1|137=7.99|A=A|79=Jason|80=5|10=228|'''
    assert parse_message(formatted) == expected, pprint(parse_message(formatted))

    # ||

    formatted = '''8=FIX.4.2|9=156|35=J|49=PXMD|56=Q037|34=2|52=20140922-14:48:49.825|73=3|11=C11111|37=O11111|11=C22222|37=O22222|37=O33333|78=2|79=Marcin|80=10|136=1|137=7.99|22||79=Jason|80=5|10=228|'''
    assert parse_message(formatted) == expected, pprint(parse_message(formatted))

    # |9001=12345|

    formatted = '''8=FIX.4.2|9=156|35=J|49=PXMD|56=Q037|34=2|9001=12345|52=20140922-14:48:49.825|73=3|11=C11111|37=O11111|11=C22222|37=O22222|37=O33333|78=2|79=Marcin|80=10|136=1|137=7.99|79=Jason|80=5|10=228|'''
    expected['Field9001'] = '12345'
    assert parse_message(formatted) == expected, pprint(parse_message(formatted))
    del expected['Field9001']

    # note, we still don't have a test where the group breaks by a rogue tag mid-group
    # is that something necessary? at that point, it's pretty badly broken.

    # Bad BeginString 8=FIX.

    formatted = '''8=FIX.|9=156|35=J|49=PXMD|56=Q037|34=2|52=20140922-14:48:49.825|73=3|11=C11111|37=O11111|11=C22222|37=O22222|37=O33333|78=2|79=Marcin|80=10|136=1|137=7.99|79=Jason|80=5|10=228|'''
    original = expected.pop('BeginString')
    assert parse_message(formatted) == dict(expected, BeginString='FIX.'), pprint(parse_message(formatted))

    # put BeginString back
    expected['BeginString'] = original

    # note, we chop off the CheckSum here because we're gonna mess it up badly
    formatted = '''8=FIX.4.2|9=156|35=X|49=PXMD|56=Q037|34=2|52=20140922-14:48:49.825|73=3|11=C11111|37=O11111|11=C22222|37=O22222|37=O33333|78=2|79=Marcin|80=10|136=1|137=7.99|79=Jason|80=5|'''
    checksum = expected.pop('CheckSum')

    # update MsgType
    expected['MsgType'] = 'X'

    assert parse_message(formatted) != expected, pprint(parse_message(formatted))
    assert parse_message(formatted, cls=FIX.FIX42.Allocation) == expected, pprint(parse_message(formatted))

    # put those fields back to how they were

    expected['MsgType'] = 'J'
    expected['CheckSum'] = checksum

    expected = {
        'BeginString': 'FIX.4.2',
        'BodyLength': '74',
        'CheckSum': '213',
        'EncryptMethod': '1',
        'HeartBtInt': '3503',
        'MsgType': 'A',
        'RawData': 'AAAAAAAAAAAAAAAA\001AAA',
        'RawDataLength': '20',
        'SendingTime': '20150407-04:12:54.885'}

    # we're messing with Logon RawData and RawDataLength, disparity between purpoted length and data
    # behavior should observe the length field, and ignore bytes unaccounted for

    # RawDataLength < len(RawData)

    expected['RawDataLength'] = '17'

    formatted = '8=FIX.4.2\0019=74\00135=A\00152=20150407-04:12:54.885\00198=1\001108=3503\00195=%s\00196=AAAAAAAAAAAAAAAA\001AAA\00110=213\001' % (expected['RawDataLength'], )
    assert parse_message(formatted) == expected, pprint(parse_message(formatted))

    # RawDataLength > len(RawData)
    # We lose CheckSum tag to RawData

    expected['RawDataLength'] = '23'    #TODO should we not expect to handle overlylong values here?
    expected['RawData'] = 'AAAAAAAAAAAAAAAA\001AAA\00110=213'
    expected.pop('CheckSum')

    formatted = '8=FIX.4.2\0019=74\00135=A\00152=20150407-04:12:54.885\00198=1\001108=3503\00195=%s\00196=AAAAAAAAAAAAAAAA\001AAA\00110=213\001' % (expected['RawDataLength'], )
    assert parse_message(formatted) == expected, pprint(parse_message(formatted))


def test_initialize():
    
    m = FIX.FIX42.NewOrderSingle()
    m.initialize()

    for field in m._all.itervalues():
        if field.required:
            assert field in m
            assert m.get(field).value, field.name + ' not initialized'
    
    expected = {
         'BeginString': 'FIX.4.2',
         'BodyLength': '312',
         'CheckSum': '206',
         'MsgSeqNum': '2',
         'MsgType': 'i',
         'NoQuoteSets': [{'NoQuoteEntries': [{'BidSize': '1000000',
                                              'BidSpotRate': '1.4363',
                                              'OfferSize': '900000',
                                              'OfferSpotRate': '1.4365',
                                              'QuoteEntryID': '0'},
                                             {'BidSize': '7000000',
                                              'BidSpotRate': '1.4363',
                                              'OfferSize': '800000',
                                              'OfferSpotRate': '1.4365',
                                              'QuoteEntryID': '1'}],
                          'QuoteSetID': '123'},
                         {'NoQuoteEntries': [{'BidSize': '1000000',
                                              'BidSpotRate': '1.4363',
                                              'OfferSize': '900000',
                                              'OfferSpotRate': '1.4365',
                                              'QuoteEntryID': '2'},
                                             {'BidSize': '7000000',
                                              'BidSpotRate': '1.4363',
                                              'OfferSize': '800000',
                                              'OfferSpotRate': '1.4365',
                                              'QuoteEntryID': '3'}],
                          'QuoteSetID': '234'}],
         'QuoteID': '1',
         'SenderCompID': 'PXMD',
         'SendingTime': '20140922-14:48:49.825',
         'Signature': 'TestSignature',
         'TargetCompID': 'Q037'}

    data = {'NoQuoteSets': expected.pop('NoQuoteSets')}
    data['SendingTime'] = expected.pop('SendingTime')
    data['Signature'] = expected.pop('Signature')
    
    m = FIX.FIX42.MassQuote(**expected)
    m.initialize(**data)

    for field in m._all.itervalues():
        if field.required:
            assert field.name in m
            assert m.get(field).value, field.name + ' not initialized'

    # don't assert repr/str, as intialize order will be different
    # also, we can't achieve 100% code coverage with this test as we'd need
    # to supply optional=True
    expected.update(data)
    assert parse_message(str(m)) == expected, pprint(parse_message(str(m)))

    m = FIX.FIX42.Logon()
    m.initialize(HeartBtInt=60, optional=True)

    for field in m.header._all:
        if field in ('BeginString', 'BodyLength', 'SenderCompID',
                     'TargetCompID', 'MsgSeqNum', ):
            continue
        assert field in m.header._initialized

    for field in m._all:
        assert field in m._initialized

    for field in m.trailer._all:
        if field == 'CheckSum':
            continue
        assert field in m.trailer._initialized

    assert m.get(FIX.FIX42.Logon.HeartBtInt).value == 60


def test_helpers():
    assert FIX.get_field_name(35) == 'MsgType'
    assert FIX.get_field_name('35') == 'MsgType'
    assert FIX.get_field_number('MsgType') == '35'

    assert FIX.get_field_name(11) == 'ClOrdID'
    assert FIX.get_field_name('11') == 'ClOrdID'
    assert FIX.get_field_number('ClOrdID') == '11'

    assert FIX.get_message_name('A') == 'Logon'
    assert FIX.get_message_name('D') == 'NewOrderSingle'


def test_generators():
    assert FIX.FIX42.NewOrderSingle.ClOrdID.generate_value()
    assert FIX.FIX42.NewOrderSingle.ClOrdID().value

    assert not FIX.FIX42.NewOrderSingle.ClOrdID(default=False).value
    assert FIX.FIX42.NewOrderSingle.ClOrdID(default=lambda **kw: 1).value == 1

    assert FIX.FIX42.NewOrderSingle.Symbol().value.isupper()
    assert len(FIX.FIX42.NewOrderSingle.Symbol().value) in range(1, 5)
