# -*- coding: utf-8 -*-
'''
phixlib.fix
~~~~~~~~~~~

Internal phixlib classes. Normally you don't need anything from here
other than FIX. Only use these classes if you know what you're doing.

    >>> from phixlib import FIX

'''
from collections import OrderedDict
from itertools import imap, izip_longest
from xml.etree import ElementTree

from .generators import GENERATORS


__all__ = ['FIX']


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class FIXRegistry(AttrDict):
    '''
    Do not initialize this class yourself. To use this class, do:

    >>> from phixlib import FIX

    '''

    _versions = set()

    def __repr__(self):
        versions = sorted(list(self._versions))
        if versions:
            return "<FIXRegistry: %s>" % (
                ', '.join(['FIX::%s' % (v, ) for v in versions]), )
        else:
            return "<FIXRegistry>"

    def register_version(self, xmlfile):
        '''
        Read a FIX data dictionary (a specification), and generate
        `Field`, `Group`, and `Message` types. These types are then
        registered and accessible via dict or attribute-like access.

        >>> FIX.register_version('FIX42.xml')

        >>> FIX.FIX42.NewOrderSingle
        <class 'FIX.FIX42.NewOrderSingle'>

        >>> FIX['FIX.4.2']['NewOrderSingle']
        <class 'FIX.FIX42.NewOrderSingle'>

        Note, the following are registered automatically:

            * FIX42.xml
            * FIX43.xml
            * FIX44.xml

        '''
        def iterchildren(element, version):
            for child in element:
                name = child.get('name')
                required = True if child.get('required') == 'Y' else False

                if child.tag == 'field':
                    field = FIXMeta._registry[version].get(name)
                    attrib = field.__dict__.copy()
                    attrib.update(required=required)

                    # __mro__ ends up looking like:
                    #
                    # Tag, Tag, Field, object, type
                    #
                    # however Tag above is two distinct id's, this one
                    # and the one retrieved from the registry

                    yield type(name, (field, ), attrib)

                elif child.tag == 'group':
                    fields = OrderedDict()
                    fields.update((f.name, f) for f in iterchildren(child, version))

                    group = FIXMeta._registry[version].get(name)
                    attrib = group.__dict__.copy()
                    attrib.update(required=required, _all=fields)

                    # __mro__ = Tag, Group, Tag, Field, object, type

                    yield type(name, (Group, group, ), attrib)

                elif child.tag == 'component':
                    # Components are just fields, groups, and other
                    # components. Simply expand them as we encounter them.
                    # Note, we don't actually parse out Component objects.
                    path = "./components/component[@name='{0}']".format(name)
                    component = root.find(path)
                    for f in iterchildren(component, version):
                        yield f

        if isinstance(xmlfile, basestring) and xmlfile.startswith('<'):
            root = ElementTree.fromstring(xmlfile)

        elif isinstance(xmlfile, (basestring, file)) or xmlfile.endswith('.xml'):
            root = ElementTree.parse(xmlfile).getroot()

        version = "{type}.{major}.{minor}".format(**root.attrib)

        for field in root.findall('./fields/field'):
            name = field.get('name')
            enums = OrderedDict((v.get('enum'), v.get('description')) for v in
                                field.findall('./value'))
            attrib = {k.strip(): v.strip() for k, v in field.attrib.iteritems()}
            attrib.update(enums=enums, version=version)
            cls = type(name, (Field, ), attrib)

        for field in root.findall('./header'):
            fields = OrderedDict((f.name, f) for f in iterchildren(field, version))
            attrib = {'_all': fields, 'version': version}
            cls = type('Header', (FIXHeader, ), attrib)

        for field in root.findall('./trailer'):
            fields = OrderedDict((f.name, f) for f in iterchildren(field, version))
            attrib = {'_all': fields, 'version': version}
            cls = type('Trailer', (FIXTrailer, ), attrib)

        for message in root.findall('./messages/message'):
            name = message.get('name')
            fields = OrderedDict((f.name, f) for f in iterchildren(message, version))
            attrib = {k.strip(): v.strip() for k, v in message.attrib.iteritems()}
            attrib.update(_all=fields, version=version)
            cls = type(name, (FIXMessage, ), attrib)

    def get_field_number(self, field, version='FIX.4.2'):
        try:
            return self[version][str(field)].number
        except KeyError:
            pass

    def get_field_name(self, field, version='FIX.4.2'):
        try:
            return self[version].Fields[str(field)].name
        except KeyError:
            pass

    def get_message_name(self, msgtype, version='FIX.4.2'):
        try:
            return self[version].Messages[str(msgtype)].name
        except KeyError:
            pass

    def get_message_type(self, name, version='FIX.4.2'):
        try:
            return self[version].Messages[str(name)].msgtype
        except KeyError:
            pass

class FIXMeta(type):
    _registry = FIXRegistry()

    def __new__(mcs, name, bases, d):
        _registry = FIXMeta._registry

        # If we're initializing a new FIXMessage or Group, set _all
        # fields as class attributes in the message.

        basenames = [base.__name__ for base in bases]

        if set(['FIXMessage', 'FIXHeader', 'FIXTrailer', 'Group']) & set(basenames):
            d.update(dict(d.get('_all', {})))

        # Set enums as class attributes, should only apply to fields...

        d.update({v: k for k, v in d.get('enums', {}).iteritems()})

        if 'Field' in basenames and 'Group' not in basenames:
            if name in GENERATORS:
                method = classmethod(GENERATORS[name])
                d['generate_value'] = method
            elif 'type' in d and d['type'] in GENERATORS:
                method = classmethod(GENERATORS[d['type']])
                d['generate_value'] = method

        if name == 'FIXMessage':
            d['msgtype'] = None
            d['msgcat'] = None
            d['name'] = None
            d['_all'] = OrderedDict()
            d['__module__'] = 'FIX.FIX42'

            new_class = super(FIXMeta, mcs).__new__(mcs, name, bases, d)

            if 'FIXMessage' not in FIXMeta._registry:
                _registry['FIXMessage'] = new_class

            return new_class

        else:
            new_class = super(FIXMeta, mcs).__new__(mcs, name, bases, d)

        version = d.pop('version', 'FIX.4.2')
        _registry._versions.add(version.replace('.', ''))

        # register both dotted and dot-less notation of the FIX version
        # so we can call both FIX.FIX42 and FIX['FIX.4.2'].

        registry = _registry.setdefault(version, AttrDict())
        registry = _registry.setdefault(version.replace('.', ''), registry)

        # Only register fields in the registry, not fields defined in a message
        # or repeating tag. This has a side effect that you can't specifically
        # get a tag associated with a particular message directly from the
        # registry. Instead, you would do something like:
        # FIX.FIX42.NewOrderSingle.OrdType

        if name not in registry:
            registry[name] = new_class

        if 'FIXMessage' in _registry and 'FIXMessage' not in registry:
            cls = super(FIXMeta, mcs).__new__(
                mcs, 'FIXMessage', (_registry['FIXMessage'], ),
                {'version': version,
                 '__module__': 'FIX.' + version.replace('.', '')
                })
            registry['FIXMessage'] = cls

        if 'Field' in basenames:
            fields = registry.setdefault('Fields', AttrDict())
            fields[new_class.number] = new_class
            fields[int(new_class.number)] = new_class

        if 'FIXMessage' in basenames:
            new_class.Header = _registry[version].Header
            new_class.Trailer = _registry[version].Trailer

            messages = registry.setdefault('Messages', AttrDict())
            messages[name] = new_class
            messages[new_class.msgtype] = new_class

        if name in ('Header', 'Trailer') and 'FIXMessage' in _registry[version]:
            setattr(_registry[version].FIXMessage, name, new_class)
            if not hasattr(_registry.FIXMessage, 'Header'):
                setattr(_registry.FIXMessage, name, new_class)
            if not hasattr(_registry.FIXMessage, 'Trailer'):
                setattr(_registry.FIXMessage, name, new_class)

        setattr(new_class, '__module__', 'FIX.' + version.replace('.', ''))

        return new_class

    def __call__(cls, *args, **kwargs):
        '''
        If user calls FIX.FIX42.FIXMessage() and they supply a valid
        MsgType for the FIX version, call that class constructor instead.

        >>> type(FIX.FIX42.FIXMessage(MsgType='D'))
        <class 'FIX.FIX42.NewOrderSingle'>

        >>> type(FIX.FIX42.FIXMessage(MsgType='D', BeginString='FIX.4.4'))
        <class 'FIX.FIX44.NewOrderSingle'>
        '''

        if cls.__name__ == 'FIXMessage' and 'MsgType' in kwargs:
            version = kwargs.get('BeginString', cls.__module__[4:])
            _registry = FIXMeta._registry
            _registry = _registry.get(version, _registry.get('FIX.4.2'))
            cls = _registry.Messages.get(kwargs['MsgType'], cls)
        return super(FIXMeta, cls).__call__(*args, **kwargs)


FIX = FIXMeta._registry


class FIXMixIn(object):
    '''
    A MixIn class for providing various getters and setters, along with
    container methods.

    '''

    def __contains__(self, item):
        '''
        Check if item is initialized in message. Item can be a tag,
        name, or number.
        '''
        if isinstance(item, (basestring, int)) and not str(item).isdigit():
            return item in self._initialized

        elif isinstance(item, (basestring, int)) and str(item).isdigit():
            return any(f for f in self._initialized.itervalues() if f.number == str(item))

        elif isinstance(item, type) and issubclass(item, Field):
            return item.name in self._initialized

        elif isinstance(item, Field):
            # check identity versus equaity, as we want to be sure
            # changing item gets changed in the message
            return item.name in self._initialized and \
                item is self._initialized[item.name]

        else:
            return False

    def __iadd__(self, other):
        ''' 
        Don't think I want to maintain this API.

        '''#XXX
        if isinstance(other, Field) and other.name not in self._initialized:
            self._initialized[other.name] = other
        return self

    def __isub__(self, other):
        ''' 
        Don't think I want to maintain this API.

        '''#XXX
        if isinstance(other, Field) and other.name in self._initialized:
            if other == self._initialized[other.name]:
                self._initialized.pop(other.name)
        return self

    def set(self, tag, *args, **kwargs):
        '''
        Set a tag in the Message. If tag is a name or number a new Tag
        instance will be initialized with `args` and `kwargs` passed
        to the tag's `Field` constructor.

        :param tag:
        :returns: A `phixlib.Field`
        '''
        # if this is an instance, just place it there outright, even if
        # the tag does not belong in this message

        if isinstance(tag, Field):
            self._initialized[tag.name] = tag
            return tag

        if isinstance(tag, (basestring, int)) and str(tag).isdigit():
            tag = str(tag)
            for field in self._initialized.itervalues():
                if field.number == tag:
                    break
            else:
                field = None

        elif isinstance(tag, basestring) and not str(tag).isdigit():
            field = self._initialized.get(tag)

        elif isinstance(tag, type) and issubclass(tag, Field):
            field = self._initialized.get(tag.name)

        # field was already set, it's not a group, we can just change in place

        if field and len(args) == 1 and not isinstance(field, type):
            field.value = args[0]
            return field

        # no field, we need to initialize it

        if not field:

            # get the class

            if isinstance(tag, type) and issubclass(tag, Field):
                tag = tag.name

            for field in self._all.itervalues():
                if str(tag) in (field.name, field.number):
                    break
            else:
                field = None

        if field:
            field = self._initialized[field.name] = field(*args, **kwargs)
            return field

        if bool(kwargs.get('ignore_spec')) is True:

            version = getattr(self, 'version', self.__module__[4:])
            _registry = FIXMeta._registry[version]
            field = _registry.get(str(tag), _registry.Fields.get(str(tag)))

            if field:
                field = self._initialized[field.name] = field(*args, **kwargs)

        return field

    def get(self, tag):
        '''
        Get a tag by name or number.

        :param tag:
        :returns: A `phixlib.Field` or None
        '''
        if isinstance(tag, (basestring, int)) and str(tag).isdigit():
            tag = str(tag)
            for field in self._initialized.itervalues():
                if field.number == tag:
                    return field

        elif isinstance(tag, basestring) and not str(tag).isdigit():
            return self._initialized.get(tag)

        elif isinstance(tag, type) and issubclass(tag, Field):
            return self._initialized.get(tag.name)

        elif isinstance(tag, Field):
            return self._initialized.get(tag.name)

        else:
            return


class FIXHeader(FIXMixIn):
    '''
    A FIX Header component.

    :members: _all, _initialized, _message, mutations

    '''

    __metaclass__ = FIXMeta

    def __init__(self, message=None, *args, **kwargs):
        self._initialized = OrderedDict()
        self._message = message

        # we loop over _all items in order because the spec says so

        for name, tag in self._all.iteritems():
            if name in kwargs:
                value = kwargs[name]
                field = tag(value)
                self._initialized[name] = field

        # try to guess the msgtype from the message

        if 'MsgType' not in kwargs and message is not None:
            self._initialized['MsgType'] = self.MsgType(message.msgtype)

        self.mutations = {}

    def __iter__(self):
        for field in _flatten(*self._initialized.itervalues()):
            yield field

    def __repr__(self):
        m = []

        # BeginString is ALWAYS FIRST FIELD IN MESSAGE (always unencrypted)

        m.append(repr(self._initialized.get('BeginString',
            self.BeginString(self.version))))

        # BodyLength is ALWAYS SECOND FIELD IN MESSAGE (always unencrypted)

        length = len(self._message)
        m.append(repr(self.BodyLength(length)))

        # MsgType is ALWAYS THIRD FIELD IN MESSAGE (always unencrypted)

        m.append(repr(self._initialized.get('MsgType',
            self.MsgType(self._message.msgtype))))

        for name, field in self._initialized.iteritems():
            # BeginString and BodyLength are added later, MsgType
            # already added (and included in BodyLength calculation
            if name in ('BeginString', 'BodyLength', 'MsgType'):
                continue
            m.append(repr(field))

        return ''.join(m)

    def __str__(self):
        m = []

        # BeginString is ALWAYS FIRST FIELD IN MESSAGE (always unencrypted)

        m.append(str(self._initialized.get('BeginString',
            self.BeginString(self.version))))

        # BodyLength is ALWAYS SECOND FIELD IN MESSAGE (always unencrypted)

        length = len(self._message)
        m.append(str(self.BodyLength(length)))

        # MsgType is ALWAYS THIRD FIELD IN MESSAGE (always unencrypted)

        m.append(str(self._initialized.get('MsgType',
            self.MsgType(self._message.msgtype))))

        for name, field in self._initialized.iteritems():
            # BeginString and BodyLength are added later, MsgType
            # already added (and included in BodyLength calculation
            if name in ('BeginString', 'BodyLength', 'MsgType'):
                continue
            m.append(str(field))

        return ''.join(m)

    def initialize(self, optional=False, **kwargs):
        '''
        Initializes a FIXHeader, with optionally supplied kwargs.

        The following fields cannot be initialized through this method:

            - BeginString
            - BodyLength
            - MsgType
            - SenderCompID
            - TargetCompID
            - MsgSeqNum

        '''
        for name, field in self._all.iteritems():
            if name in self._initialized:
                continue

            if name in ('BeginString', 'BodyLength', 'MsgType',
                        'SenderCompID', 'TargetCompID', 'MsgSeqNum'):
                continue

            if field.required or optional or name in kwargs:
                if name in kwargs:
                    self._initialized[name] = field(kwargs[name], **kwargs)

                else:
                    self._initialized[name] = field(**kwargs)

        return


class FIXTrailer(FIXMixIn):
    '''
    A FIX Trailer component.

    :members: _all, _initialized, _message, mutations

    '''

    __metaclass__ = FIXMeta

    def __init__(self, message=None, *args, **kwargs):
        self._initialized = OrderedDict()
        self._message = message

        # we loop over _all items in order because the spec says so

        for name, tag in self._all.iteritems():
            if name in kwargs:
                value = kwargs[name]
                field = tag(value)
                self._initialized[name] = field

        self.mutations = {}

    def __iter__(self):
        for field in _flatten(*self._initialized.itervalues()):
            if field.name == 'CheckSum':
                continue
            yield field

    def __repr__(self):
        return ''.join(imap(repr, self))

    def __str__(self):
        return ''.join(imap(str, self))

    def initialize(self, optional=False, **kwargs):
        '''
        Initializes a FIXTrailer, with optionally supplied kwargs.

        The following fields cannot be initialized through this method:

            - CheckSum

        '''
        for name, field in self._all.iteritems():
            if name in self._initialized:
                continue

            if name in ('CheckSum', ):
                continue

            if field.required or optional or name in kwargs:
                if name in kwargs:
                    self._initialized[name] = field(kwargs[name], **kwargs)

                else:
                    self._initialized[name] = field(**kwargs)

        return


class FIXMessage(FIXMixIn):
    '''

    :members: header, trailer, name, msgtype, mutations,
        _all, _initialized, _parser, _version

    '''

    __metaclass__ = FIXMeta

    def __init__(self, *args, **kwargs):
        self.header = self.Header(self, *args, **kwargs)
        self.trailer = self.Trailer(self, *args, **kwargs)
        self._initialized = OrderedDict()

        # we loop over _all items in order because the spec says so

        for name, tag in self._all.iteritems():
            if issubclass(tag, (Group, )) and \
                    (name in kwargs or set(kwargs) & set(tag._all)):

                # Call kwargs.get here, as the group tag may not have
                # been explicitly passed as a keyword arg. If it is
                # specified though, we'll set the value in the kwarg
                # as that group tag's value.

                field = tag(*kwargs.get(name, []), **kwargs)
                self._initialized[name] = field

            elif name in kwargs:
                value = kwargs[name]
                field = tag(value)
                self._initialized[name] = field

        self.mutations = {}

    def __iter__(self):
        '''
        Iterate over each tag in the message, excluding the CheckSum.
        '''
        for field in self.header:
            yield field
        for field in _flatten(*self._initialized.itervalues()):
            yield field
        for field in self.trailer:
            yield field

    def __len__(self):
        '''
        Calculates the true BodyLength of the message.
        '''
        length = 0
        for field in self:
            if field.name in ('BeginString', 'BodyLength', 'CheckSum'):
                continue
            length += len(str(field))
        return length

    def __repr__(self):
        '''
        Format this message in a human-readable form (SOH delimiters
        are represented as the pipe '|' character).
        '''
        # We do this twice, once with str and once with repr. str is used
        # to get the actual value of the CheckSum field, without inflating
        # our ordinal sum with a pipe.
        m = "{0}{1}{2}".format(self.header,
            ''.join(imap(str, _flatten(*self._initialized.itervalues()))),
            self.trailer)

        r = "{0}{1}{2}".format(repr(self.header),
            ''.join(imap(repr, _flatten(*self._initialized.itervalues()))),
            repr(self.trailer))

        r += repr(self.trailer.CheckSum('%03d' % (sum(bytearray(m)) % 256, )))
        return r

    def __str__(self):
        '''
        Format this message for consumption by a FIX engine.
        '''
        m = "{0}{1}{2}".format(self.header,
            ''.join(imap(str, _flatten(*self._initialized.itervalues()))),
            self.trailer)
        m += str(self.trailer.CheckSum('%03d' % (sum(bytearray(m)) % 256, )))
        return m

    @classmethod
    def fromstring(cls, message, parse_message=None, **kwargs):
        '''
        Parses *message* using parser, and returns a `FIXMessage`.

        :param message: A raw FIX message.
        :param parse_message: By default, `phixlib.parser.parse_message`
            is used.

        :returns: A `FIXMessage` from *string*.
        '''

        parse_message = parse_message or getattr(cls, '_parser', parse_message)

        if not parse_message:
            from .parser import parse_message
            setattr(cls, '_parser', staticmethod(parse_message))

        parts = parse_message(message)
        parts.update(kwargs)

        if 'MsgType' in parts and cls is FIXMessage:
            version = parts.get('BeginString', cls.__module__[4:])
            _registry = FIXMeta._registry[cls.__module__[4:]]
            _registry = FIXMeta._registry.get(version, _registry)
            cls = _registry.Messages.get(parts['MsgType'], cls)

        return cls(**parts)

    def initialize(self, optional=False, **kwargs):
        '''
        Initializes a FIXMessage, with optionally supplied kwargs.
        '''
        self.header.initialize(optional=optional, **kwargs)

        for name, field in self._all.iteritems():
            if name in self._initialized:
                continue

            if field.required or optional or name in kwargs:
                if issubclass(field, (Group, )) and \
                    (name in kwargs or set(kwargs) & set(field._all)):

                    # Call kwargs.get here, as the group tag may not have
                    # been explicitly passed as a keyword arg. If it is
                    # specified though, we'll set the value in the kwarg
                    # as that group tag's value.

                    field = field(*kwargs.get(name, []), **kwargs)
                    self._initialized[name] = field

                elif name in kwargs:
                    self._initialized[name] = field(kwargs[name], **kwargs)

                else:
                    self._initialized[name] = field(**kwargs)

        self.trailer.initialize(optional=optional, **kwargs)
        return


class Field(object):
    '''
    A FIX Field object. Control creation of a Field with a spec
    conforming value by supplying *default* keyword argument when
    value is `None`. If *default* is a callable object, it will be
    called with kwargs arguments. If *default* is a bool, the
    `generate_value` method will be called. By default, *default*
    is True (a value will be generated for this Field if `value`
    supplied is None).

    :members: name, number, value, enums, mutations

    '''

    __metaclass__ = FIXMeta

    def __init__(self, value=None, *args, **kwargs):
        if value is None:
            default = kwargs.get('default', True)

            if callable(default):
                value = default(**kwargs)
            elif bool(default):
                value = self.generate_value(**kwargs)

        self.value = value
        self.mutations = {}
        self._group = kwargs.get('_group')

    def __repr__(self):
        '''
        Format this field in a human-readable form (SOH delimiters
        are represented as the pipe '|' character).
        '''
        value = '' if self.value is None else self.value
        return "{0}={1}|".format(self.number, value)

    def __str__(self):
        '''
        Format this field for consumption by a FIX engine.
        '''
        value = '' if self.value is None else self.value
        return "{0}={1}\001".format(self.number, value)

    @classmethod
    def generate_value(self, **kwargs):
        return ''

    def __eq__(self, other):
        if self.name != other.name:
            return False
        if self.number != other.number:
            return False
        if self.value != other.value:
            return False
        return True

    @property
    def group(self):
        return self._group


class Group(object):
    '''
    A `Group` is simply a container for repeating fields. On its own
    it represents the number of repeating group instances following it.

    :members: name, number, value, mutations,
        _all, _initialized

    '''

    __metaclass__ = FIXMeta

    def __init__(self, *args, **kwargs):
        '''
        To initialize a repeating group, supply a list of dict.
        '''
        self._initialized = []

        # the following code will normalize keyword arguments
        # passed from a web query (args will be empty)...

        keys = set(self._all) & set(kwargs)

        if not args and keys:
            for key in keys:
                if not isinstance(kwargs[key], (list, tuple)):
                    continue

                args = [dict(zip(keys, v)) for v in
                        izip_longest(*(kwargs[k] for k in keys))]
                break

            else:
                args = [{key: kwargs[key] for key in keys}]

        for kw in args:
            group = []

            # we loop over _all items in order because the spec says so

            for name, tag in self._all.iteritems():
                if issubclass(tag, (Group, )) and \
                        (name in kw or set(kw) & set(tag._all)):

                    # Call .get() here, as the group tag may not have
                    # been explicitly passed as a keyword arg. If it is
                    # specified though, we'll set the value in the kwarg
                    # as that group tag's value.

                    field = tag(*kw.get(name, []), _group=self, **kwargs)

                elif name in kw:
                    value = kw[name]
                    field = tag(value, _group=self)

                else:
                    continue

                group.append(field)

            if group:
                self._initialized.append(group)

        if not self._initialized and kwargs.get('default', True):
            group = []
            for tag in self._all.itervalues():
                if tag.required:
                    kwargs.pop('_group', None)
                    group.append(tag(_group=self, *args, **kwargs))
            else:
                self._initialized.append(group)

        self.mutations = {}
        self._group = kwargs.get('_group')

    def __repr__(self):
        '''
        Format this field in a human-readable form (SOH delimiters
        are represented as the pipe '|' character).
        '''
        return "{0}={1}|".format(self.number, self.value)

    def __str__(self):
        '''
        Format this field for consumption by a FIX engine.
        '''
        return "{0}={1}\001".format(self.number, self.value)

    def __contains__(self, item):
        return item in self._initialized

    def __iter__(self):
        for fields in self._initialized:
            for field in fields:
                yield field

    def __getitem__(self, key):
        return self._initialized[key]

    def __setitem__(self, key, value):
        self._initialized[key] = value

    def __delitem__(self, key):
        del self._initialized[key]

    def __len__(self):
        return len(self._initialized)

    @property
    def group(self):
        '''
        This property is used within a repeating Group. The nested
        repeating group will maintain a reference to its parent
        group through this property.
        '''
        return self._group

    @property
    def value(self):
        return len(self._initialized)

    def initialize(self, optional=False, **kwargs):
        '''
        Initializes a Group, with optionally supplied kwargs.
        '''

        for name, field in self._all.iteritems():
            if name in self._initialized:
                continue

            if field.required or optional or name in kwargs:
                if issubclass(field, (Group, )) and \
                    (name in kwargs or set(kwargs) & set(field._all)):

                    # Call kwargs.get here, as the group tag may not have
                    # been explicitly passed as a keyword arg. If it is
                    # specified though, we'll set the value in the kwarg
                    # as that group tag's value.

                    field = field(*kwargs.get(name, []), **kwargs)
                    self._initialized[name] = field

                elif name in kwargs:
                    self._initialized[name] = field(kwargs[name], **kwargs)

                else:
                    self._initialized[name] = field(**kwargs)

        self.trailer.initialize(optional=optional, **kwargs)
        return


def _flatten(*args):
    for arg in args:
        if hasattr(arg, '__iter__'):
            yield arg
            for arg_ in _flatten(*arg):
                yield arg_
        else:
            yield arg
