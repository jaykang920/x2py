import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

from x2py import __version__

class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ''

    def run_tests(self):
        import shlex
        import pytest
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)

setup(
    name='x2py',
    version=__version__,
    description='Python port of x2',
    url='https://github.com/jaykang920/x2py',
    author='Jae-jun Kang',
    author_email='jaykang920@gmail.com',
    license='MIT',
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    packages=[
        'x2py',
        'x2py.flows',
        'x2py.links',
        'x2py.links.asyncio',
        'x2py.links.asyncore',
        'x2py.transforms',
        'x2py.util',
        'x2py.yields',
        'xpiler',
    ],
    scripts=['scripts/x2py.xpiler.py']
)