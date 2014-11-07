===============
django-postgres
===============

I'm aware there is a kickstarter (django.contrib.postgres).

This is kind-of a parallel project, for me to play around with some ideas I have about using some really nice postgres features.

.. note:: This app requires django 1.7 or greater, and postgres 9.4 or greater (for JSONB/fancy JSONB operators), both of which are currently in beta.

Fields (stable-ish)
===================

There are already some fields that are mostly ready to use.

ArrayField
----------
A backport of `django.contrib.postgres`' `ArrayField`.

BigIntField
-----------
A wrapper on `IntegerField` that uses the postgres `bigint` column type. Does nothing else.

CompositeField
--------------
A parent class for creating your own Composite Types.

http://schinckel.net/2014/09/24/using-postgres-composite-types-in-django/

This generally requires that either the composite type already exists in your database, or you write a migration (using the supplied migration Operation, as then it will handle late registration).

Documentation for this is probably poorer than it needs to be to be usable.

IntervalField
-------------
Super-simple interval field that maps to a python timedelta.


JSONField
---------
Actually a JSONB field, that seamlessly handles JSON data, converting it to and from python `dict`, `list` and relevant primitives, via in-built json handling from psycopg2 and python.

This allows for lookups using the new django 1.7 lookup API:

    >>> MyModel.objects.filter(field__0__lt=2)
    >>> MyModel.objects.filter(field__has_all=['a', 'b'])

It supports all of the json operators: containment, contains, equality, has all, has any. It also supports the path lookup operators, although will not work with keys with characters that are not part of the character set that makes up python identifiers, or contain a double underscore.

The bottom of http://schinckel.net/2014/05/25/querying-json-in-postgres/ contains more information about how it may eventually work. The lookups work, but the names of them may change.

RangeField(s)
-------------
Seamless handling (including form fields, and widgets) of the default Range types supplied by Postgres.

A range field contains a start and a finish, and flags if the upper and lower bounds are inclusive or not. These bounds are rendered as the mathematical notation for bounds inclsivity: `[`, `(` for the lower bound, and `]`, `)` for the upper bound. You probably don't want to be showing this to non-mathematically literate users.

UUIDField
---------
Simple UUIDField that takes advantage of psycopg2's uuid handling facilities.

Fields you probably don't need to use
=====================================

OIDField
--------
A subclass of `IntegerField` that writes the column type as `oid`. This is an internal postgres column type: you probably don't want to use this.


Fields (development)
====================

RruleField
----------
Had an idea to do this. Made some progress, however it's likely to be too slow to use python in postgres the way I have.

Extras
======

postgres.audit
--------------

What should be a useful auditing system. Uses postgres `AFTER UPDATE` triggers to log changes to a table. Working relatively well, so far.

Uses a middleware to set the django user id (and external ip address), which are stored in session variables.

postgres.search
---------------

A search feature, built using postgres `VIEW`s, that allow selecting data from disparate tables (using `UNION ALL`). I really need to finish the blog post about this.

I've currently got this working using the really neat search widget from `UIKit`.

sql.json_ops
------------

A couple of extra functions/operators for PG9.4's json/jsonb datatypes. These bring it up to almost parity with hstore, or should eventually.

Notably, it allows for `subtraction` of json objects, or subtraction from a json object of an array of strings. This operation is used in the `postgres.audit` trigger function to remove unwanted/unchanged column values.

sql.benchmark
-------------

A neat function for benchmarking postgres function execution time. Probably not useful to you, but might be.