from setuptools import setup

from version import version

setup(
    name='x2py',
    version=version,
    description='Python port of x2',
    url='https://github.com/jaykang920/x2py',
    author='Jae-jun Kang',
    author_email='jaykang920@gmail.com',
    license='MIT',
    packages=[
        'x2py',
        'x2py.flows',
        'x2py.links',
        'x2py.links.asyncio',
        'x2py.links.asyncore',
        'x2py.transforms',
        'x2py.util',
        'xpiler',
    ],
    scripts=['scripts/x2py.xpiler.py']
)