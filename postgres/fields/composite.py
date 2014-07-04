from django.db.models import fields
from django.db import connection

from psycopg2.extras import register_composite, CompositeCaster
from psycopg2.extensions import register_adapter, adapt, AsIs


class CompositeMeta(type):
    def __init__(cls, name, bases, clsdict):
        super(CompositeMeta, cls).__init__(name, bases, clsdict)
        cls.register_composite()

    def register_composite(cls):
        db_type = cls().db_type(connection)
        if db_type:
            cls.python_type = register_composite(
                db_type,
                connection.cursor().cursor,
                globally=True
            ).type

            def adapt_composite(composite):
                return AsIs("(%s)::%s" % (
                    ", ".join([
                        adapt(getattr(composite, field)).getquoted() for field in composite._fields
                    ]), db_type
                ))

            register_adapter(cls.python_type, adapt_composite)


class CompositeField(fields.Field):
    __metaclass__ = CompositeMeta
    """
    A handy base class for defining your own composite fields.

    It registers the composite type.
    """

