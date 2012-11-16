# -*- coding: utf-8 *-*

import unittest
from pypfp.core import Field, Record
from pypfp.core import FixedEngine
from pypfp.converters import Float, Int, String, DateTime
import os


class Foo(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __eq__(self, other):
        return type(self) is type(other) and \
               set(self.__dict__.items()) == set(other.__dict__.items())

    def __repr__(self):
        return ' '.join([str(k) + ': ' + str(v)
                    for k, v in self.__dict__.items()])


class FooA(Foo):
    pass


class FooB(Foo):
    pass


class TestRecordDefinition(unittest.TestCase):

    def setUp(self):
        self.example = Record(Foo, fill='?')
        self.example.add_field(Field('name', 0, 10, String))
        self.example.add_field(Field('age', 10, 2, Int))
        self.example.add_field(Field('salary', 12, 14, Float, precision=4))

    def test_init(self):
        self.assertFalse(self.example._initiated)
        self.assertEquals(len(self.example.fields), 3)
        self.assertIsNone(self.example.string_format)
        self.example.init()
        self.assertTrue(self.example)
        self.assertIsNotNone(self.example.string_format)

    def test_line_generation(self):
        f = Foo(name='ariel', age=32, salary=123.45)
        s = self.example.to_string(f)
        self.assertEquals('ariel     32000000123.4500', s)

    def test_line_generation_with_padchar(self):
        f = Foo(name='ariel', age=32, salary=123.45)
        self.example.fields[1].start += 2
        self.example.fields[2].start += 2
        s = self.example.to_string(f)
        self.assertEquals('ariel     ??32000000123.4500', s)

    def test_value_recover_with_padchar(self):
        string = 'ariel     ??32000000123.4500'
        self.example.fields[1].start += 2
        self.example.fields[2].start += 2
        f = self.example.to_value(string)
        self.assertEqual(f.name, 'ariel')
        self.assertEqual(f.age, 32)
        self.assertEqual(f.salary, 123.45)

    def test_value_recover_with_instance(self):
        string = 'ariel     32000000123.4500'
        f = self.example.to_value(string)
        self.assertEqual(f.name, 'ariel')
        self.assertEqual(f.age, 32)
        self.assertEqual(f.salary, 123.45)


class TestField(unittest.TestCase):

    def setUp(self):
        self.name = Field('name', 0, 10, truncate=True, fill='P')
        self.age = Field('age', 10, 4, Int)
        self.a = Foo()
        self.a.name = 'ariel'
        self.a.age = 32

    def test_init(self):
        self.assertEquals(self.name.name, 'name')
        self.assertEquals(self.name.start, 0)
        self.assertEquals(self.name.width, 10)
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
        f = Field('name', 0, 10)
        self.a.name = 'ariel rossanigo'
        self.assertRaises(ValueError, f.to_string, self.a)

    def test_to_string_too_large_with_truncate(self):
        self.a.name = 'ariel rossanigo'
        self.assertEquals(self.name.to_string(self.a), 'ariel ross')


class TestFixedEngine(unittest.TestCase):

    def setUp(self):
        self.record_a = Record(FooA, [
                    Field('type', 0, 2, Int),
                    Field('name', 2, 10, String),
                    Field('age', 12, 2, Int),
                    Field('salary', 14, 14, Float, precision=4)
                                    ])

        self.record_b = Record(FooB, [
                    Field('type', 0, 2, Int),
                    Field('address', 2, 10, String, truncate=True),
                    Field('phone', 12, 20, String)
                                        ])

        d = {'01': self.record_a, '02': self.record_b}
        self.selector = lambda x: d[x[0:2]]

        self.objs = []
        self.objs.append(FooA(type=1, name='ariel', age=32, salary=123.45))
        self.objs.append(FooB(type=2, address='galvez 60', phone='1234-234'))
        self.objs.append(FooB(type=2, address='rafaela -', phone='1234-234'))
        self.objs.append(FooA(type=1, name='lorena', age=30, salary=678.99))
        self.objs.append(FooB(type=2, address=u'áÑ¡¿ü', phone='1234-234'))
        self.objs.append(FooB(type=2, address='rafaela -', phone='1234-234'))

    def test_init_with_one_record(self):
        r = FixedEngine([self.record_a])
        self.assertEquals(len(r.records), 1)
        self.assertIs(r.records[0], self.record_a)
        self.assertIs(r.selector('anything'), self.record_a)
        obj = FooA()
        self.assertIs(r.find_record(obj), self.record_a)

    def test_init_with_two_records_custom_selector(self):
        self.assertRaises(AssertionError, FixedEngine,
                                                [self.record_a, self.record_b])
        r = FixedEngine([self.record_a, self.record_b], self.selector)
        obj_a = FooA()
        obj_b = FooB()
        self.assertEquals(len(r.records), 2)
        self.assertIs(r.records[0], self.record_a)
        self.assertIs(r.records[1], self.record_b)
        self.assertIs(r.selector('01Ariel'), self.record_a)
        self.assertIs(r.selector('02Ariel'), self.record_b)
        self.assertIs(r.find_record(obj_a), self.record_a)
        self.assertIs(r.find_record(obj_b), self.record_b)

    def test_init_with_two_records_using_selector_string(self):
        self.assertRaises(AssertionError, FixedEngine,
                                                [self.record_a, self.record_b])
        self.record_a.selector_string = u'01'
        self.record_b.selector_string = u'02'

        r = FixedEngine([self.record_a, self.record_b], selector_slice=(0, 2))
        obj_a = FooA()
        obj_b = FooB()
        self.assertEquals(len(r.records), 2)
        self.assertIs(r.records[0], self.record_a)
        self.assertIs(r.records[1], self.record_b)
        self.assertIs(r.selector('01Ariel'), self.record_a)
        self.assertIs(r.selector('02Ariel'), self.record_b)
        self.assertIs(r.find_record(obj_a), self.record_a)
        self.assertIs(r.find_record(obj_b), self.record_b)

    def test_save(self):
        f = FixedEngine([self.record_a, self.record_b], self.selector)
        fi = 'samples/test_sample1.txt'
        f.save(fi, self.objs)
        self.assertTrue(os.path.exists(fi))
        lines1 = open(fi, 'r').readlines()
        lines2 = open('samples/sample_utf8.txt', 'r').readlines()
        self.assertEquals(''.join(lines1), ''.join(lines2))
        os.remove(fi)

    def test_load(self):
        f = FixedEngine([self.record_a, self.record_b], self.selector)
        objects = f.load('samples/sample_utf8.txt')
        self.assertEqual(len(objects), len(self.objs))
        for y, t in zip(objects, self.objs):
            self.assertEqual(y, t)






