# -*- coding: utf-8 *-*


class Converter(object):

    def __init__(self, length):
        self.length = length

    def to_string(self, value):
        raise NotImplementedError()  # pragma: no cover

    def to_value(self, string):
        raise NotImplementedError()  # pragma: no cover


class IntConverter(Converter):

    def to_string(self, value):
        return ('%0' + str(self.length) + 'd') % value

    def to_value(self, string):
        return int(string)


class FloatConverter(Converter):

    def __init__(self, length, decimal_places, decimal_separator=''):
        super(FloatConverter, self).__init__(length)
        self.decimal_places = decimal_places
        self.decimal_separator = decimal_separator

    def to_string(self, value):
        l = self.length + (1 if self.decimal_separator == '' else 0)
        s = '%0' + str(l) + '.' + str(self.decimal_places) + 'f'
        s = s % value
        s = s.replace('.', self.decimal_separator)
        return s

    def to_value(self, string):
        i = self.length - self.decimal_places
        if self.decimal_separator != '':
            s = string[:i - 1] + '.' + string[i:]
        else:
            s = string[:i] + '.' + string[i:]
        return float(s)

