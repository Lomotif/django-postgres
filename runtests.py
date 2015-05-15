#!/usr/bin/env python

import os
import sys

from django.conf import settings
from django.core.management import execute_from_command_line
import django

if django.VERSION < (1, 6):
    extra_settings = {
        'TEST_RUNNER': 'discover_runner.DiscoverRunner',
    }
else:
    extra_settings = {}

try:
    from psycopg2cffi import compat
    compat.register()
except ImportError:
    pass


if not settings.configured:
    settings.configure(
        INSTALLED_APPS=(
            'postgres',
            'tests',
            ),
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.postgresql_psycopg2",
                "NAME": 'django-postgres-{ENVNAME}'.format(**os.environ),
                "PORT": os.environ.get('DB_PORT', 5432),
                "SERIALIZE": False,
            }
        },
        MIDDLEWARE_CLASSES=(),
        **extra_settings
    )


def runtests():
    argv = sys.argv[:1] + ['test', '--noinput', 'tests']
    execute_from_command_line(argv)


if __name__ == '__main__':
    runtests()
