# -*- coding: utf-8 *-*

from converters import *
import codecs


class Record(object):

    def __init__(self, record_class, fields=None, fill=u' '):
        self.fields = fields if fields else []
        self.record_class = record_class
        self.fill = fill
        self.string_format = None
        self._initiated = False

    def add_field(self, field):
        self.fields.append(field)

    def init(self):
        self.fields.sort(key=lambda x: x.start)
        cur_pos = 0
        res = []
        for field in self.fields:
            #fill
            c = field.start - cur_pos
            if c > 0:
                res.append(self.fill * c)
            #add format field
            res.append(u'{:%d}' % field.width)
            cur_pos = field.start + field.width
        self.string_format = u''.join(res)
        self._initiated = True

    def to_string(self, obj):
        if not self._initiated:
            self.init()
        return self.string_format.format(*[x.to_string(obj)
                                            for x in self.fields])

    def to_value(self, line):
        obj = self.record_class()
        for field in self.fields:
            s = line[field.start:field.start + field.width]
            v = field.to_value(s)
            setattr(obj, field.name, v)
        return obj


class Field(object):

    def __init__(self, name, start, width, converter_class=String,
                 **converter_params):
        self.name = name
        self.start = start
        self.width = width
        self.converter = converter_class(width, **converter_params)

    def to_string(self, obj):
        v = getattr(obj, self.name)
        return self.converter.to_string(v)

    def to_value(self, string):
        return self.converter.to_value(string)


class FixedEngine(object):

    def __init__(self, records, selector=None):
        assert len(records) == 1 or len(records) > 1 and selector is not None
        self.records = records
        self.record_dict = {r.record_class.__name__: r for r in self.records}

        if selector is None:
            r = records[0]
            self.selector = lambda x: r
        else:
            self.selector = selector

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




