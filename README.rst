===============
django-postgres
===============

I'm aware there is a kickstarter (django.contrib.postgres).

This is kind-of a parallel project, for me to play around with some ideas I have about using some really nice postgres features.

.. note:: This app requires django 1.7 or greater, and postgres 9.4 or greater (for JSONB/fancy JSONB operators), both of which are currently in beta.

Fields (stable-ish)
===================

There are already some fields that are mostly ready to use.

BigIntField
-----------
A wrapper on `IntegerField` that uses the postgres `bigint` column type. Does nothing else.

JSONField
---------
Actually a JSONB field, that seamlessly handles JSON data, converting it to and from python `dict`, `list` and relevant primitives, via in-built json handling from psycopg2 and python.

This allows for lookups using the new django 1.7 lookup API:

    >>> MyModel.objects.filter(field__0__lt=2)
    >>> MyModel.objects.filter(field__has_all=['a', 'b'])

It supports all of the json operators: containment, contains, equality, has all, has any. It also supports the path lookup operators, although will not work with keys with characters that are not part of the character set that makes up python identifiers, or contain a double underscore.

UUIDField
---------
Simple UUIDField that takes advantage of psycopg2's uuid handling facilities.

OIDField
--------
A subclass of `IntegerField` that writes the column type as `oid`. This is an internal postgres column type: you probably don't want to use this.

Fields (development)
====================

IntervalField
-------------
Should be easy to develop, based on my django-timedeltafield.

RangeField(s)
-------------
This may be tricky.

RruleField
----------
Had an idea to do this. Made some progress, however it's likely to be too slow to use python in postgres the way I have.

Extras
======

postgres.audit
--------------

What should be a useful auditing system. Uses postgres AFTER UPDATE triggers to log changes to a table. Working relatively well, so far.

Uses a middleware to set the django user id (and external ip address), which could be the weak link, as these are put into a temporary table, that should only last as long as the current transaction. Since this happens in middleware, we may lose it if the request contains multiple transactions.

sql.json_ops
------------

A couple of extra functions/operators for PG9.4's json/jsonb datatypes. These bring it up to almost parity with hstore, or should eventually.

Notably, it allows for `subtraction` of json objects, or subtraction from a json object of an array of strings. This operation is used in the `postgres.audit` trigger function to remove unwanted/unchanged column values.

sqs.benchmark
-------------

A neat function for benchmarking postgres function execution time. Probably not useful to you, but might be.