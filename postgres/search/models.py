from django.db import models

import postgres.fields


class SearchQuerySet(models.QuerySet):
    def matches(self, search_term):
        search_term = '%s:*' % search_term.lower()

        return self.filter(term__matches=search_term).extra(select={
            'rank': "ts_rank(term, to_tsquery(%s))",
        }, select_params=(search_term,)).order_by('-rank')


class Search(models.Model):
    term = postgres.fields.TSVectorField()
    title = models.TextField()
    detail = models.TextField()
    url_name = models.TextField()
    url_kwargs = postgres.fields.JSONField()
    # url_name?

    objects = SearchQuerySet.as_manager()

    class Meta:
        managed = False
