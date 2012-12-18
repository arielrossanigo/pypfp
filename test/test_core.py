# -*- coding: utf-8 *-*

import unittest
from pypfp.core import Field, Record
from pypfp.core import FixedEngine
from pypfp.converters import Float, Int, String  # , DateTime
import os
import datetime

class Foo(Record):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __eq__(self, other):
        return type(self) is type(other) and \
               set(self.__dict__.items()) == set(other.__dict__.items())

    def __repr__(self):
        return ' '.join([str(k) + ': ' + str(v)
                    for k, v in self.__dict__.items()])


class RecordA(Foo):
    typ = Field(Int, 2)
    name = Field(String, 10, default=u'default')
    age = Field(Int, 2, default=lambda: datetime.datetime.today().day)
    salary = Field(Float, 14, precision=4)

    class Meta:
        selector_string = u'01'


class RecordB(Foo):
    typ = Field(Int, 2)
    address = Field(String, 10, truncate=True)
    phone = Field(String, 20)

    class Meta:
        selector_string = u'02'


class TestRecordDefinition(unittest.TestCase):

    def setUp(self):
        class Example(Record):
            name = Field(String, 10)
            age = Field(Int, 2)
            salary = Field(Float, 14, precision=4)

        class Example2(Record):
            name = Field(String, 10, start=0, default=u'ariel')
            age = Field(Int, 2, start=12)
            salary = Field(Float, 14, start=14, precision=4)

            class Meta:
                fill = u'?'

        self.example = Example
        self.example2 = Example2

        self.f1 = Example()
        self.f1.name = 'ariel'
        self.f1.age = 32
        self.f1.salary = 123.45

        self.f2 = Example2()
        self.f2.age = 32
        self.f2.salary = 123.45

    def test_init(self):
        self.assertEquals(len(self.example._record_options.fields), 3)
        self.assertIsNotNone(self.example._record_options.string_format)

    def test_line_generation(self):
        s = self.example.to_string(self.f1)
        self.assertEquals('ariel     32000000123.4500', s)

    def test_line_generation_with_padchar(self):
        s = self.example2.to_string(self.f2)
        self.assertEquals('ariel     ??32000000123.4500', s)

    def test_value_recover_with_padchar(self):
        string = 'ariel     ??32000000123.4500'
        f = self.example2.to_value(string)
        self.assertEqual(f.name, self.f2.name)
        self.assertEqual(f.age, self.f2.age)
        self.assertEqual(f.salary, self.f2.salary)

    def test_value_recover_with_instance(self):
        string = 'ariel     32000000123.4500'
        f = self.example.to_value(string)
        self.assertEqual(f.name, 'ariel')
        self.assertEqual(f.age, 32)
        self.assertEqual(f.salary, 123.45)
        self.assertEqual(type(f), self.example)

    def test_default(self):
        a = RecordA()
        d = datetime.datetime.today().day
        self.assertEqual(a.age, d)
        self.assertEqual(a.name, u'default')


class TestField(unittest.TestCase):

    def setUp(self):
        self.name = Field(String, 10, name='name', start=0, fill='P',
                          truncate=True, default=u'default')
        self.age = Field(Int, 4, name='age', start=10)
        self.a = Foo()
        self.a.name = 'ariel'
        self.a.age = 32

    def test_init(self):
        self.assertEquals(self.name.name, 'name')
        self.assertEquals(self.name.start, 0)
        self.assertEquals(self.name.width, 10)
        self.assertEquals(self.name.converter.default, u'default')

        self.assertIsInstance(self.name.converter, String)
        self.assertTrue(self.name.converter.truncate)
        self.assertEquals(self.name.converter.fill, 'P')
        self.assertEquals(self.name.width, 10)

    def test_string_to_string(self):
        self.assertEqual(self.name.to_string(self.a), 'arielPPPPP')

    def test_int_to_string(self):
        self.assertEqual(self.age.to_string(self.a), '0032')

    def test_to_value_string(self):
        f = Foo()
        self.name.to_value('arielPPPPP', f)
        self.assertEqual(f.name, self.a.name)

    def test_to_value_int(self):
        f = Foo()
        self.age.to_value('0032', f)
        self.assertEqual(f.age, self.a.age)

    def test_to_string_defaults_too_large(self):
        f = Field(String, 10, name='name', start=0)
        self.a.name = 'ariel rossanigo'
        self.assertRaises(ValueError, f.to_string, self.a)

    def test_to_string_too_large_with_truncate(self):
        self.a.name = 'ariel rossanigo'
        self.assertEquals(self.name.to_string(self.a), 'ariel ross')


class TestFixedEngine(unittest.TestCase):

    def setUp(self):

        d = {'01': RecordA, '02': RecordB}
        self.selector = lambda x: d[x[0:2]]

        self.objs = []

        self.objs.append(RecordA(typ=1, name='ariel', age=32, salary=123.45))
        self.objs.append(RecordB(typ=2, address='galvez 60', phone='1234-234'))
        self.objs.append(RecordB(typ=2, address='rafaela -', phone='1234-234'))
        self.objs.append(RecordA(typ=1, name='lorena', age=30, salary=678.99))
        self.objs.append(RecordB(typ=2, address=u'áÑ¡¿ü', phone='1234-234'))
        self.objs.append(RecordB(typ=2, address='rafaela -', phone='1234-234'))

    def test_init_with_one_record(self):
        r = FixedEngine([RecordA])
        self.assertEquals(len(r.records), 1)
        self.assertIs(r.records[0], RecordA)
        self.assertIs(r.selector('anything'), RecordA)
        obj = RecordA()
        self.assertIs(r.find_record(obj), RecordA)

    def test_init_with_two_records_custom_selector(self):
        self.assertRaises(AssertionError, FixedEngine, [RecordA, RecordB])
        r = FixedEngine([RecordA, RecordB], self.selector)
        obj_a = RecordA()
        obj_b = RecordB()
        self.assertEquals(len(r.records), 2)
        self.assertIs(r.records[0], RecordA)
        self.assertIs(r.records[1], RecordB)
        self.assertIs(r.selector('01Ariel'), RecordA)
        self.assertIs(r.selector('02Ariel'), RecordB)
        self.assertIs(r.find_record(obj_a), RecordA)
        self.assertIs(r.find_record(obj_b), RecordB)

    def test_init_with_two_records_using_selector_string(self):
        self.assertRaises(AssertionError, FixedEngine, [RecordA, RecordB])
        r = FixedEngine([RecordA, RecordB], selector_slice=(0, 2))
        obj_a = RecordA()
        obj_b = RecordB()
        self.assertEquals(len(r.records), 2)
        self.assertIs(r.records[0], RecordA)
        self.assertIs(r.records[1], RecordB)
        self.assertIs(r.selector('01Ariel'), RecordA)
        self.assertIs(r.selector('02Ariel'), RecordB)
        self.assertIs(r.find_record(obj_a), RecordA)
        self.assertIs(r.find_record(obj_b), RecordB)

    def test_save(self):
        f = FixedEngine([RecordA, RecordB], self.selector)
        fi = 'samples/test_sample1.txt'
        f.save(fi, self.objs)
        self.assertTrue(os.path.exists(fi))
        lines1 = open(fi, 'r').readlines()
        lines2 = open('samples/sample_utf8.txt', 'r').readlines()
        self.assertEquals(''.join(lines1), ''.join(lines2))
        os.remove(fi)

    def test_load(self):
        f = FixedEngine([RecordA, RecordB], self.selector)
        objects = f.load('samples/sample_utf8.txt')
        self.assertEqual(len(objects), len(self.objs))
        for y, t in zip(objects, self.objs):
            self.assertEqual(y, t)






