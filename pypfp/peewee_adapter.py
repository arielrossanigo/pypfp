# -*- coding: utf-8 -*-

import peewee
from pypfp.core import Field, RecordMetaClass, Record
from pypfp.converters import Int, DateTime, String, Float


class PeeweeRecordMetaClass(peewee.BaseModel, RecordMetaClass):

    def __new__(cls, name, bases, attrs):
        _r = cls.get_record_options(attrs)
        records = [(k, v) for k, v in attrs.items() if isinstance(v, Field)]
        for k, v in records:
            attrs[k] = cls.get_db_field(v)

        res = super(PeeweeRecordMetaClass, cls).__new__(cls, name,
                                                            bases, attrs)
        res._record_options = _r
        return res

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


class PeeweeRecord(peewee.Model, Record):
    __metaclass__ = PeeweeRecordMetaClass



