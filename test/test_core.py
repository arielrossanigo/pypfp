# -*- coding: utf-8 *-*

import unittest
from pypfp.core import FieldDefinition, RecordDefinition
from pypfp.converters import FloatConverter, IntConverter


class Foo(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


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

    def test_to_string_with_float_connector(self):
        f = FieldDefinition('test', 0, 10, FloatConverter(10, 4, ''))
        obj = Foo()
        obj.test = -123.56
        self.assertEquals('-001235600', f.to_string(obj))

