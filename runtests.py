#!/usr/bin/env python

import os, sys

from django.conf import settings
import django

try:
    from psycopg2cffi import compat
    compat.register()
except ImportError:
    pass

DEFAULT_SETTINGS = dict(
    INSTALLED_APPS=(
        'postgres',
        'postgres.tests',
        ),
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": "postgres-fields",
        }
    },
    MIDDLEWARE_CLASSES=()
)


def runtests():
    if not settings.configured:
        settings.configure(**DEFAULT_SETTINGS)

    if hasattr(django, 'setup'):
        django.setup()
        from django.test.runner import DiscoverRunner
        runner_class = DiscoverRunner
    else:
        from django.test.utils import get_runner
        runner_class = get_runner(settings)

    parent = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, parent)

    test_args = ['postgres']

    failures = runner_class(
        verbosity=1, interactive=True, failfast=False).run_tests(test_args)
    sys.exit(failures)


if __name__ == '__main__':
    runtests()
