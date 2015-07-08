from pypfp.core import Field, Record
from pypfp.core import FixedEngine
from pypfp.converters import Float, Int, String


class Header(Record):
    typ = Field(Int, 2)
    name = Field(String, 10)
    age = Field(Int, 2)
    salary = Field(Float, 14, precision=4)

    class Meta:
        selector_string = u'01'


class Address(Record):
    typ = Field(Int, 2)
    address = Field(String, 10, truncate=True)
    phone = Field(String, 20)

    class Meta:
        selector_string = u'02'

# read sample file
engine = FixedEngine([Header, Address], selector_slice=(0, 2))

# print records
for r in engine.load('../samples/sample_utf8.txt'):
    print unicode(r).encode('utf-8')
