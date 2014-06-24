from django.db import models

from postgres.fields import json_field

class Search(models.Model):
    term = models.TextField()
    title = models.TextField()
    detail = models.TextField()
    url_name = models.TextField()
    url_kwargs = json_field.JSONField()
    # url_name?

    class Meta:
        managed = False
