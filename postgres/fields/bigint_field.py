from django.db.models.fields import IntegerField

class BigIntField(IntegerField):
    description = "Big Integer Field"

    def db_type(self, connection):
        return 'bigint'
