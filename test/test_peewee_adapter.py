# -*- coding: utf-8 -*-

from unittest import TestCase
import peewee
from pypfp.peewee_adapter import PeeweeRecord
from pypfp.core import Field, FixedEngine
from pypfp.converters import Float, Int, String


class BaseRecord(PeeweeRecord):
    client_id = peewee.IntegerField()

    class Meta:
        database = peewee.SqliteDatabase('test.db')


class RecordA(BaseRecord):
    typ = Field(Int, 2)
    name = Field(String, 10)
    age = Field(Int, 2)
    salary = Field(Float, 14, precision=4)

    class Meta:
        selector_string = u'01'


stack = lambda x: x + 1


class RecordB(BaseRecord):
    typ = Field(Int, 2)
    address = Field(String, 10, truncate=True)
    phone = Field(String, 20)

    class Meta:
        selector_string = u'02'
        stack_function = stack
        fill = u'?'


class TestPeeweeAdapter(TestCase):

    def test_record_generation(self):
        self.assertEquals(RecordA._record_options.selector_string, u'01')
        self.assertEquals(RecordA._record_options.fill, u' ')
        self.assertEquals(len(RecordA._record_options.fields), 4)

        self.assertEquals(RecordB._record_options.selector_string, u'02')
        self.assertEquals(RecordB._record_options.fill, u'?')
        self.assertIs(RecordB._record_options.stack_function, stack)
        self.assertEquals(len(RecordB._record_options.fields), 3)

    def test_example(self):
        RecordA.drop_table(fail_silently=True)
        RecordB.drop_table(fail_silently=True)
        RecordA.create_table(fail_silently=True)
        RecordB.create_table(fail_silently=True)

        f = FixedEngine([RecordA, RecordB], selector_slice=(0, 2))
        client_id = 0
        aux = []
        for r in f.load('samples/sample_utf8.txt'):
            if type(r) is RecordA:
                client_id += 1
            r.client_id = client_id
            if type(r) is RecordB:
                aux.append(r)
            r.save()

        c1 = RecordA.get(client_id=1)
        self.assertEquals(c1.typ, 1)
        self.assertEquals(c1.name, u'ariel')
        self.assertEquals(c1.age, 32)
        self.assertEquals(c1.salary, 123.45)

        self.assertEquals(RecordA.select().count(), 2)

        c2 = RecordB.select()
        self.assertEquals(c2.count(), 4)

        for y, t in zip(c2, aux):
            self.assertEquals(y.typ, t.typ)
            self.assertEquals(y.address, t.address)
            self.assertEquals(y.phone, t.phone)




