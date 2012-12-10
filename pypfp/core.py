# -*- coding: utf-8 *-*

from converters import *
import codecs


class Field(object):
    order = 0

    @staticmethod
    def get_order():
        Field.order += 1
        return Field.order

    def __init__(self, converter_class, width, start=None, name=None,
                 **converter_params):
        self.order = Field.get_order()
        self.name = name
        self.start = start
        self.width = width
        self.converter = converter_class(width, **converter_params)

    def to_string(self, obj):
        v = getattr(obj, self.name)
        return self.converter.to_string(v)

    def to_value(self, string, obj):
        v = self.converter.to_value(string)
        setattr(obj, self.name, v)


class RecordOptions(object):

    def __init__(self, fill=u' ', selector_string=u'', stack_function=None):
        self.fields = []
        self.fill = fill
        self.selector_string = selector_string
        if stack_function is None:
            self.stack_function = lambda x: x + 1
        else:
            self.stack_function = stack_function


class RecordMetaClass(type):

    meta_confs = ('fill', 'selector_string', 'stack_function')

    def __new__(cls, name, bases, attrs):

        meta = attrs.get('Meta', None)
        meta_options = {}
        if meta:
            meta_options.update((k, v) for k, v in meta.__dict__.items()
                                        if k in RecordMetaClass.meta_confs)
#                                        if not k.startswith('_'))
        _record_options = RecordOptions(**meta_options)
        stack_function = _record_options.stack_function

        records = [(k, v) for k, v in attrs.items() if isinstance(v, Field)]
        records.sort(key=lambda x: x[1].order)

        formats = []
        last_pos = -1
        for k, v in records:
            v.name = k
            if v.start is None:
                v.start = stack_function(last_pos)
            to_fill = v.start - last_pos - 1
            if to_fill > 0:
                formats.append(_record_options.fill * to_fill)
            formats.append(u'{:%d}' % v.width)
            last_pos = v.start + v.width - 1
            _record_options.fields.append(v)
            attrs[k] = None
        _record_options.string_format = u''.join(formats)

        attrs['_record_options'] = _record_options
        return super(RecordMetaClass, cls).__new__(cls, name, bases, attrs)


class Record(object):
    __metaclass__ = RecordMetaClass

    @classmethod
    def to_string(cls, obj):
        return cls._record_options.string_format.format(*[x.to_string(obj)
                                        for x in cls._record_options.fields])

    @classmethod
    def to_value(cls, line):
        obj = cls()
        for field in cls._record_options.fields:
            s = line[field.start:field.start + field.width]
            field.to_value(s, obj)
        return obj


class FixedEngine(object):

    def __init__(self, records, selector=None, selector_slice=None):
        self.records = records
        self.record_dict = {r.__name__: r for r in self.records}

        if selector is not None:
            self.selector = selector
        elif selector_slice is not None:
            _x, _y = selector_slice
            d = {r._record_options.selector_string: r for r in records}
            self.selector = lambda s: d[s[_x:_y]]
        elif len(records) == 1:
            r = records[0]
            self.selector = lambda s: r
        else:
            raise AssertionError('No selector provided')

    def save(self, path, objects, encoding='utf-8'):
        lines = []
        for obj in objects:
            record = self.find_record(obj)
            lines.append((record.to_string(obj)).encode(encoding))

        with open(path, 'w') as f:
            f.write('\n'.join(lines))

    def load(self, path, encoding='utf-8'):
        lines = codecs.open(path, 'r', encoding).readlines()
        res = []
        for line in lines:
            record = self.selector(line)
            res.append(record.to_value(line))
        return res

    def find_record(self, obj):
        return self.record_dict[obj.__class__.__name__]

