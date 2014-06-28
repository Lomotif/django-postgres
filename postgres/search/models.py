from django.db import models

import postgres.fields


class Search(models.Model):
    term = postgres.fields.TSVectorField()
    title = models.TextField()
    detail = models.TextField()
    url_name = models.TextField()
    url_kwargs = postgres.fields.JSONField()
    # url_name?

    class Meta:
        managed = False
