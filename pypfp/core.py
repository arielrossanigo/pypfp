# -*- coding: utf-8 *-*

from converters import *


class RecordDefinition(object):

    def __init__(self, record_class, fields=None, padchar=' '):
        self.fields = fields if fields else []
        self.record_class = record_class
        self.padchar = padchar
        self.string_format = None
        self._initiated = False

    def add_field(self, field):
        self.fields.append(field)

    def init(self):
        self.fields.sort(key=lambda x: x.start)
        cur_pos = 0
        res = []
        for field in self.fields:
            #fill with padchar
            c = field.start - cur_pos
            if c > 0:
                res.append(self.padchar * c)
            #add format field
            res.append('{:%d}' % field.length)
            cur_pos = field.start + field.length
        self.string_format = ''.join(res)
        self._initiated = True

    def to_string(self, obj):
        if not self._initiated:
            self.init()
        print self.string_format
        return self.string_format.format(*[x.to_string(obj)
                                            for x in self.fields])

    def to_value(self, line):
        obj = self.record_class()
        for field in self.fields:
            s = line[field.start:field.start + field.length]
            v = field.to_value(s)
            setattr(obj, field.name, v)
        return obj


class FieldDefinition(object):

    aligns = {
                '<': lambda s, c: s.rstrip(c),
                '^': lambda s, c: s.strip(c),
                '>': lambda s, c: s.lstrip(c)
            }

    def __init__(self, name, start, length, converter=None,
                 padchar=' ', align='<'):
        self.name = name
        self.start = start
        self.length = length
        self.converter = converter
        self.padchar = padchar
        self.align = align
        self.format = '{:%s%s%d}' % (self.padchar.strip(), self.align,
                                    self.length)

    def to_string(self, obj):
        v = getattr(obj, self.name)
        if self.converter:
            s = self.converter.to_string(v)
        else:
            s = str(v)
        return self.format.format(s)

    def to_value(self, string):
        if self.padchar != '':
            string = FieldDefinition.aligns[self.align](string, self.padchar)
        if self.converter:
            return self.converter.to_value(string)
        return string


class FixedEngine(object):

    def __init__(self, records, selectors=None):
        assert len(records) == 1 or len(records) > 1 and selectors is not None
        self.records = records
        self.selector = selector

    def save(self, path, objects):
        pass

    def load(self, path):
        pass


