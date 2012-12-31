# -*- coding: utf-8 -*-

import peewee
from pypfp.core import RecordMetaClass, Record
from pypfp.converters import Int, DateTime, String, Float, BigInt, Decimal


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
        if field.converter.db_field_class:
            return field.converter.db_field_class(
                                            **field.converter.db_field_params)
        if type(field.converter) is Int:
            return peewee.IntegerField(default=field.converter.default)
        if type(field.converter) is Decimal:
            return peewee.DecimalField(default=field.converter.default,
                                    max_digits=field.converter.width,
                                    decimal_places=field.converter.precision)
        if type(field.converter) is BigInt:
            return peewee.BigIntegerField(default=field.converter.default)
        if type(field.converter) is String:
            return peewee.CharField(max_length=field.width,
                                            default=field.converter.default)
        if type(field.converter) is Float:
            return peewee.FloatField(default=field.converter.default)
        if type(field.converter) is DateTime:
            return peewee.DateField(default=field.converter.default)
        raise ValueError('Converter without map %s' % type(field.converter))


class PeeweeRecord(peewee.Model, Record):
    __metaclass__ = PeeweeRecordMetaClass



