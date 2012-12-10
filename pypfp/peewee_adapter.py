# -*- coding: utf-8 -*-

import peewee
from pypfp.core import RecordOptions, Field
from pypfp.converters import Int, DateTime, String, Float


class PeeweeRecordMetaClass(peewee.BaseModel):

    meta_confs = ('fill', 'selector_string', 'stack_function')

    def __new__(cls, name, bases, attrs):

        meta = attrs.get('Meta', None)
        meta_options = {}
        if meta:
            for k, v in meta.__dict__.items():
                if k in PeeweeRecordMetaClass.meta_confs:
                    meta_options[k] = v
                    meta.__dict__.pop(k)

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
            attrs[k] = cls.get_db_field(v)
        _record_options.string_format = u''.join(formats)

        attrs['_record_options'] = _record_options
        return super(PeeweeRecordMetaClass, cls).__new__(cls, name,
                                                            bases, attrs)

    @staticmethod
    def get_db_field(field):
        if type(field.converter) is Int:
            if field.width < 7:
                return peewee.IntegerField()
            else:
                return peewee.BigIntegerField()
        if type(field.converter) is String:
            return peewee.CharField(max_length=field.width)
        if type(field.converter) is Float:
            return peewee.FloatField()
        if type(field.converter) is DateTime:
            return peewee.DateField()
        raise ValueError('Converter without map %s' % type(field.converter))


class PeeweeRecord(peewee.Model):
    __metaclass__ = PeeweeRecordMetaClass

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


class RecordA(PeeweeRecord):
    typ = Field(Int, 2)
    name = Field(String, 10)
    age = Field(Int, 2)
    salary = Field(Float, 14, precision=4)

    class Meta:
        selector_string = u'01'
        database = peewee.PostgresqlDatabase('wiltel', user='wiltel',
                                                            password='wiltel')


class RecordB(PeeweeRecord):
    typ = Field(Int, 2)
    address = Field(String, 10, truncate=True)
    phone = Field(String, 20)

    class Meta:
        selector_string = u'02'
        database = peewee.PostgresqlDatabase('wiltel', user='wiltel',
                                                            password='wiltel')


if __name__ == '__main__':
    from pypfp.core import FixedEngine
    RecordA.drop_table(fail_silently=True)
    RecordA.create_table(fail_silently=True)
    RecordB.drop_table(fail_silently=True)
    RecordB.create_table(fail_silently=True)
    f = FixedEngine([RecordA, RecordB], selector_slice=(0, 2))
    for r in f.load('../samples/sample_utf8.txt'):
        r.save()

