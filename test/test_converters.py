# -*- coding: utf-8 *-*
import unittest
from pypfp.converters import Int, Float, Number, String, DateTime
from datetime import datetime


class TestNumber(unittest.TestCase):

    def test_left_align_with_digit(self):
        self.assertRaises(AssertionError, Number, width=5, align='<', fill='0')

    def test_not_existed_align(self):
        self.assertRaises(AssertionError, Number, width=5, align='l')

    def test_not_existed_fill_character(self):
        self.assertRaises(AssertionError, Number, width=5, align='<', fill='')

    def test_mistake_with_fill_and_sign(self):
        self.assertRaises(AssertionError, Number, width=5, align='>', fill='-')

    def test_len_of_null_string(self):
        self.assertRaises(AssertionError, Number, width=5, null_string='lol')


class TestInt(unittest.TestCase):

    def _test(self, value, string, **params):
        c = Int(**params)
        s2 = c.to_string(value)
        self.assertEquals(s2, string)
        self.assertEquals(c.to_value(s2), value)

    def test_positive_number_to_left(self):
        self._test(10, '10---', width=5, align='<', fill='-')

    def test_negative_number_to_left(self):
        self._test(-10, '-10--', width=5, align='<', fill='-')

    def test_negative_number_to_rigth(self):
        self._test(-10, '00-10', width=5)

    def test_negative_number_to_rigth_with_sign_in_left(self):
        self._test(-10, '-0010', width=5, align='=')

    def test_null_string(self):
        self._test(None, 'NULL', width=4, align='=', null_string='NULL')

    def test_None_without_null_string(self):
        self.assertRaises(ValueError, self._test, None, 'NULL', width=4)

    def test_cero(self):
        self._test(0, '0000', width=4)


class TestFloat(unittest.TestCase):

    def _test(self, value, string, **params):
        c = Float(**params)
        s2 = c.to_string(value)
        self.assertEquals(s2, string)
        self.assertEquals(c.to_value(s2), value)

    def test_no_separator_with_left_align(self):
        self.assertRaises(AssertionError, Float, width=14,
                            decimal_separator='', align='<')

    def test_positive_float_with_separator(self):
        self._test(12.34, '0012.3400', precision=4, width=9)

    def test_negative_float_with_separator(self):
        self._test(-12.34, '0-12.3400', precision=4, width=9)

    def test_negative_float_without_separator(self):
        self._test(-12.34, '00-123400', precision=4, width=9,
                    decimal_separator='')

    def test_negative_float_with_left_align(self):
        self._test(-12.34, '-12.3400 ', precision=4, width=9, align='<',
                                        fill=' ')

    def test_negative_float_on_rigth_with_sign_in_left(self):
        self._test(-12.34, '- 12.3400', precision=4, width=9, align='=',
                                        fill=' ')

    def test_null_string(self):
        self._test(None, 'NULL', width=4, align='=', null_string='NULL')

    def test_negative_float_with_comma_as_separator(self):
        self._test(-12.34, '-12,3400 ', precision=4, width=9, align='<',
                                        fill=' ', decimal_separator=',')

    def test_cero(self):
        self._test(0, '0000.0000', precision=4, width=9, fill='0')

    def test_cero_without_separator(self):
        self._test(0, '000000000', precision=4, width=9, fill='0',
                                                        decimal_separator='')


class TestString(unittest.TestCase):

    def _test(self, value, string, **params):
        c = String(**params)
        s2 = c.to_string(value)
        self.assertEquals(s2, string)
        self.assertEquals(c.to_value(s2), value)

    def test_left_align(self):
        self._test('hola', 'hola ', width=5)

    def test_truncate_false(self):
        self.assertRaises(ValueError, self._test, 'hola', 'ho', width=3)

    def test_truncate_true(self):
        c = String(width=2, truncate=True)
        s2 = c.to_string('hola')
        self.assertEquals(s2, 'ho')
        self.assertEquals(c.to_value(s2), 'ho')


class TestDateTime(unittest.TestCase):

    def _test(self, value, string, **params):
        c = DateTime(**params)
        self.assertEquals(c.to_string(value), string)
        if value is not None:
            self.assertEquals(c.to_value(string),
                datetime.strptime(value.strftime(c.str_format), c.str_format))
        else:
            self.assertEquals(c.to_value(string), value)

    def setUp(self):
        self.today = datetime(2012, 11, 13, 23, 03, 52)

    def test_some_day_with_width_equal_format(self):
        self._test(self.today, '20121113', width=8, str_format='%Y%m%d')

    def test_some_day_with_width_equal_format_2(self):
        self._test(self.today, '2012/11/13 23', width=13,
                        str_format='%Y/%m/%d %H')

    def test_value_too_long(self):
        self.assertRaises(ValueError, self._test, self.today, '2012/11/13 23',
                                                width=5, str_format='%Y/%m/%d')

    def test_some_day_with_width_fill(self):
        self._test(self.today, '2012/11/13  ', width=12, str_format='%Y/%m/%d')

    def test_some_day_with_width_rigth_align(self):
        self._test(self.today, '  2012/11/13', width=12, str_format='%Y/%m/%d',
                            align='>')

    def test_null_string(self):
        self._test(None, '    /  /  ', width=12, str_format='%Y/%m/%d',
                                       null_string='    /  /  ')

    def test_none_value_not_allowed(self):
        self.assertRaises(ValueError, self._test, None, '    /  /  ', width=12,
                            str_format='%Y/%m/%d')
