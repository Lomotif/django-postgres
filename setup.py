from setuptools import setup, find_packages

from postgres import VERSION

README = open('README.rst').read()

setup(
    name='django-postgres',
    version='.'.join(map(str, VERSION)),
    description='Postgres-specific django goodness.',
    long_description=README,
    author='Matthew Schinckel',
    author_email='matt@schinckel.net',
    packages=find_packages(),
    install_requires=['Django'],
    tests_require=['Django'],
    test_suite='runtests.runtests'
)