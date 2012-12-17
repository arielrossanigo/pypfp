# -*- coding: utf-8 -*-

import peewee
from pypfp.core import RecordMetaClass, Record
from pypfp.converters import Int, DateTime, String, Float, BigInt


class PeeweeRecordMetaClass(peewee.BaseModel, RecordMetaClass):

    def __new__(cls, name, bases, attrs):
        cls.init_class(attrs, cls.get_db_field)
        _r = attrs['_record_options']
        res = super(PeeweeRecordMetaClass, cls).__new__(cls, name,
                                                            bases, attrs)
        res._record_options = _r
        return res

    @staticmethod
    def get_db_field(field):
        if field.db_field:
            return field.db_field
        if type(field.converter) is Int:
            return peewee.IntegerField()
        if type(field.converter) is BigInt:
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



