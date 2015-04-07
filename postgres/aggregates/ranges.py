from django.db.models.aggregates import Aggregate


class Normalize(Aggregate):
    template = 'normalize(array_agg(%(expression)s))'


class Missing(Aggregate):
    template = 'missing_ranges(array_agg(%(expression)s))'
