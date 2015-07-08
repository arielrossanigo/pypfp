from pypfp.core import Field
from pypfp.core import FixedEngine
from pypfp.peewee_adapter import PeeweeRecord
from pypfp.converters import Float, Int, String

from peewee import SqliteDatabase

db = SqliteDatabase('dummy.db')


class Header(PeeweeRecord):
    typ = Field(Int, 2)
    name = Field(String, 10)
    age = Field(Int, 2)
    salary = Field(Float, 14, precision=4)

    class Meta:
        selector_string = u'01'
        database = db


class Address(PeeweeRecord):
    typ = Field(Int, 2)
    address = Field(String, 10, truncate=True)
    phone = Field(String, 20)

    class Meta:
        selector_string = u'02'
        database = db

# read sample file
engine = FixedEngine([Header, Address], selector_slice=(0, 2))

# connect to db
db.connect()

# create tables
db.create_tables([Header, Address])

# write fields to db using save
for r in engine.load('../samples/sample_utf8.txt'):
    r.save()
