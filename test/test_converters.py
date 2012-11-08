# -*- coding: utf-8 *-*
import unittest
from pypfp.converters import IntConverter, FloatConverter


class TestIntConverter(unittest.TestCase):

    def setUp(self):
        self.conv = IntConverter(10)

    def test_string_convert_length(self):
        string = self.conv.to_string(10)
        self.assertEquals(len(string), 10)

    def test_string_convertion_with_positive_number(self):
        string = self.conv.to_string(10)
        self.assertEquals(string, '0000000010')

    def test_string_convertion_with_negative_number(self):
        string = self.conv.to_string(-10)
        self.assertEquals(string, '-000000010')

    def test_int_convertion_with_positive_number(self):
        val = self.conv.to_value('0000000010')
        self.assertEquals(val, 10)

    def test_int_convertion_with_negative_number(self):
        val = self.conv.to_value('-000000010')
        self.assertEquals(val, -10)


class TestFloatConverter(unittest.TestCase):

    def test_string_convert_length(self):
        conv = FloatConverter(14, 4, ',')
        string = conv.to_string(12.43)
        self.assertEquals(len(string), 14)
        self.assertEquals(string.index(','), 9)

    def test_string_convertion_with_positive_number(self):
        conv = FloatConverter(14, 4, ',')
        string = conv.to_string(123.4567)
        self.assertEquals(string, '000000123,4567')

    def test_string_convertion_without_separator(self):
        conv = FloatConverter(14, 4)
        string = conv.to_string(123.4567)
        self.assertEquals(string, '00000001234567')

    def test_string_convertion_with_negative_number(self):
        conv = FloatConverter(14, 4, '.')
        string = conv.to_string(-123.4567)
        self.assertEquals(string, '-00000123.4567')

    def test_float_convertion_with_positive_number(self):
        conv = FloatConverter(14, 4, ':')
        val = conv.to_value('000000123:4567')
        self.assertEquals(val, 123.4567)

    def test_float_convertion_without_separator(self):
        conv = FloatConverter(14, 4)
        val = conv.to_value('00000001234567')
        self.assertEquals(val, 123.4567)

    def test_float_convertion_with_negative_number(self):
        conv = FloatConverter(14, 4, ':')
        val = conv.to_value('-00000123:4567')
        self.assertEquals(val, -123.4567)

    def test_float_convertion_with_negative_number_and_without_separator(self):
        conv = FloatConverter(14, 4)
        val = conv.to_value('-0000001234567')
        self.assertEquals(val, -123.4567)
