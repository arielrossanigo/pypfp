# -*- coding: utf-8 *-*
import logging
from datetime import datetime
import decimal

_aligns = {
            '=': lambda s, f: s.lstrip(f),
            '<': lambda s, f: s.rstrip(f),
            '>': lambda s, f: s.lstrip(f),
            '^': lambda s, f: s.strip(f),
        }

logger = logging.getLogger('pypfp')


class Converter(object):

    def __init__(self, width, fill, null_string=None, default=None,
                clean_function=None):
        self.width = width
        self.null_string = null_string
        assert fill != ''
        self.fill = fill
        self.default = default
        self.clean_function = clean_function
        self.db_field_class = None
        self.db_field_params = None

    def to_string(self, value):
        raise NotImplementedError()  # pragma: no cover

    def to_value(self, string):
        raise NotImplementedError()  # pragma: no cover


class Number(Converter):

    def __init__(self, width, null_string=None, fill='0', align='>',
                default=None, clean_function=None):
        assert align in '<>='
        assert fill not in '0123456789' or align != '<'
        assert fill != '-' or align != '>'
        assert null_string is None or len(null_string) == width
        super(Number, self).__init__(width, fill, null_string, default,
                                    clean_function)
        self.align = align

    def to_string(self, value):
        if value is None and self.null_string is None:
            raise ValueError('None value not allowed')
        elif not self.null_string is None:
            return self.null_string

    def to_value(self, string):
        if string == self.null_string:
            return None
        sign = 1
        if self.align == '=' and string[0] == '-':
            string = string[1:]
            sign = -1
        string = _aligns[self.align](string, self.fill)
        return (string, sign)


class Int(Number):

    def __init__(self, width, null_string=None, fill='0', align='>',
                    default=None, clean_function=None):
        super(Int, self).__init__(width, null_string, fill, align, default,
                                clean_function)

    def to_string(self, value):
        r = super(Int, self).to_string(value)
        if r:
            return r
        try:
            return '{0:{x.fill}{x.align}{x.width}d}'.format(value, x=self)
        except Exception, e:
            logger.error(e)
            raise

    def to_value(self, string):
        r = super(Int, self).to_value(string)
        if r is None:
            return None
        string, sign = r
        if self.clean_function:
            string = self.clean_function(string)
        if string == '':
            return 0
        return int(string) * sign


class BigInt(Int):
    pass


class Float(Number):

    def __init__(self, width, null_string=None, fill='0', align='>',
                precision=6, decimal_separator='.', default=None,
                clean_function=None):
        assert decimal_separator != '' or align != '<'
        super(Float, self).__init__(width, null_string, fill, align, default,
                                    clean_function)
        self.precision = precision
        self.decimal_separator = decimal_separator

    @property
    def real_width(self):
        return self.width + (1 if self.decimal_separator == '' else 0)

    def to_string(self, value):
        r = super(Float, self).to_string(value)
        if r:
            return r
        f = '{0:{x.fill}{x.align}{x.real_width}.{x.precision}f}'
        return f.format(value, x=self).replace('.', self.decimal_separator)

    def to_value(self, string):
        r = super(Float, self).to_value(string)
        if r is None:
            return None
        string, sign = r
        if self.decimal_separator == '':
            string = string[:-self.precision] + '.' + \
                                            string[-self.precision:]
        elif self.decimal_separator != '.':
            string = string.replace(self.decimal_separator, '.')
        if self.clean_function:
            string = self.clean_function(string)
        if string in ('', '.'):
            return 0
        return float(string) * sign


class Decimal(Float):

    def to_value(self, string):
        r = super(Decimal, self).to_value(string)
        if r is None:
            return None
        return decimal.Decimal(r)


class String(Converter):

    def __init__(self, width, align='<', fill=' ', truncate=False,
                default=None, clean_function=None):
        assert align in '<>^'
        super(String, self).__init__(width, fill, None, default,
                                    clean_function)
        self.truncate = truncate
        self.align = align

    def to_string(self, value):
        string = u'{0:{x.fill}{x.align}{x.width}s}'.format(value, x=self)
        if (len(string) > self.width and not self.truncate):
            raise ValueError('Value too long: ' + string)
        return string[:self.width]

    def to_value(self, string):
        string = _aligns[self.align](string, self.fill)
        if self.clean_function:
            string = self.clean_function(string)
        return string


class DateTime(Converter):

    def __init__(self, width, str_format, null_string=None, fill=' ',
                align='<', default=None, clean_function=None):
        assert align in '<>^'
        super(DateTime, self).__init__(width, fill, null_string, default,
                                    clean_function)
        self.align = align
        self.str_format = str_format

    def to_string(self, value):
        if value is None and self.null_string is None:
            raise ValueError('None value not allowed')
        elif not self.null_string is None:
            return self.null_string
        s = value.strftime(self.str_format)
        res = '{0:{x.fill}{x.align}{x.width}s}'.format(s, x=self)
        if len(res) > self.width:
            raise ValueError('Value too long')
        return res

    def to_value(self, string):
        if string == self.null_string:
            return None
        string = _aligns[self.align](string, self.fill)
        if self.clean_function:
            string = self.clean_function(string)
        return datetime.strptime(string, self.str_format)
