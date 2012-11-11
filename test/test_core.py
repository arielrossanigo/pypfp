# -*- coding: utf-8 *-*

import unittest
from pypfp.core import FieldDefinition, RecordDefinition
from pypfp.core import FixedEngine
from pypfp.converters import FloatConverter, IntConverter
import os

class Foo(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __eq__(self, other):
        return type(self) is type(other) and \
               set(self.__dict__.items()) == set(other.__dict__.items())


class FooA(Foo):
    pass


class FooB(Foo):
    pass


class TestRecordDefinition(unittest.TestCase):

    def setUp(self):
        self.example = RecordDefinition(Foo, padchar='?')
        self.example.add_field(FieldDefinition('name', 0, 10))
        self.example.add_field(FieldDefinition('age', 10, 2, IntConverter(2)))
        self.example.add_field(FieldDefinition('salary', 12, 14,
                                        FloatConverter(14, 4, '.')))

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


class TestFieldDefinition(unittest.TestCase):

    def test_get_format_string_defaults(self):
        f = FieldDefinition('test', 0, 10)
        s = f.format
        self.assertEquals('{:<10}', s)

    def test_get_format_string_padchar(self):
        f = FieldDefinition('test', 0, 10, padchar='-')
        s = f.format
        self.assertEquals('{:-<10}', s)

    def test_get_format_string_align_center(self):
        f = FieldDefinition('test', 0, 10, padchar='-', align='^')
        s = f.format
        self.assertEquals('{:-^10}', s)

    def test_to_string_defaults(self):
        f = FieldDefinition('test', 0, 10)
        obj = Foo()
        obj.test = 'some'
        self.assertEquals('some      ', f.to_string(obj))

    def test_to_string_defaults_too_large(self):
        f = FieldDefinition('test', 0, 10)
        obj = Foo()
        obj.test = 'something too large'
        self.assertRaises(ValueError, f.to_string, obj)

    def test_to_string_too_large_with_truncate(self):
        f = FieldDefinition('test', 0, 10, truncate=True)
        obj = Foo()
        obj.test = 'something too large'
        self.assertEquals(f.to_string(obj), 'something ')

    def test_to_string_with_float_connector(self):
        f = FieldDefinition('test', 0, 10, FloatConverter(10, 4, ''))
        obj = Foo()
        obj.test = -123.56
        self.assertEquals('-001235600', f.to_string(obj))


class TestFixedEngine(unittest.TestCase):

    def setUp(self):
        self.record_a = RecordDefinition(FooA)
        self.record_a.add_field(FieldDefinition('type', 0, 2, IntConverter(2)))
        self.record_a.add_field(FieldDefinition('name', 2, 10))
        self.record_a.add_field(FieldDefinition('age', 12, 2, IntConverter(2)))
        self.record_a.add_field(FieldDefinition('salary', 14, 14,
                                                FloatConverter(14, 4, '.')))

        self.record_b = RecordDefinition(FooB)
        self.record_b.add_field(FieldDefinition('type', 0, 2, IntConverter(2)))
        self.record_b.add_field(FieldDefinition('address', 2, 10,
                                                                truncate=True))
        self.record_b.add_field(FieldDefinition('phone', 12, 20))

        d = {'01': self.record_a, '02': self.record_b}
        self.selector = lambda x: d[x[0:2]]

        self.objs = []
        self.objs.append(FooA(type=1, name='ariel', age=32, salary=123.45))
        self.objs.append(FooB(type=2, address='galvez 60', phone='1234-234'))
        self.objs.append(FooB(type=2, address='rafaela - santa fe - argentina',
                            phone='1234-234'))
        self.objs.append(FooA(type=1, name='lorena', age=30, salary=678.99))
        self.objs.append(FooB(type=2, address='galvez 60', phone='1234-234'))
        self.objs.append(FooB(type=2, address='rafaela - santa fe - argentina',
                            phone='1234-234'))

    def test_init_with_one_record(self):
        r = FixedEngine([self.record_a])
        self.assertEquals(len(r.records), 1)
        self.assertIs(r.records[0], self.record_a)
        self.assertIs(r.selector('anything'), self.record_a)
        obj = FooA()
        self.assertIs(r.find_record(obj), self.record_a)

    def test_init_with_two_records(self):
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

    def test_save(self):
        f = FixedEngine([self.record_a, self.record_b], self.selector)
        fi = 'samples/test_sample1.txt'
        f.save(fi, self.objs)
        self.assertTrue(os.path.exists(fi))
        lines1 = open(fi, 'r').readlines()
        lines2 = open('samples/sample_1.txt', 'r').readlines()
        self.assertEquals(''.join(lines1), ''.join(lines2))
        os.remove(fi)

    def test_load(self):
        f = FixedEngine([self.record_a, self.record_b], self.selector)
        objects = f.load('samples/sample_1.txt')
        self.assertEqual(len(objects), len(self.objs))
        for y, t in zip(objects, self.objs):
            self.assertEqual(y, t)




