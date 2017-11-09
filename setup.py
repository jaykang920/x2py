from setuptools import setup

setup(
    name='x2py',
    version='0.1.0',
    description='Python 3 port of x2',
    url='https://github.com/jaykang920/x2py',
    author='Jae-jun Kang',
    author_email='jaykang920@gmail.com',
    license='MIT',
    packages=[
        'x2py',
        'x2py.flows',
        'x2py.links',
        'x2py.links.asyncio',
        'x2py.util',
        'xpiler',
    ],
    scripts=['scripts/x2py.xpiler.py']
)