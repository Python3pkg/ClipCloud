#!/usr/bin/env python

import os
from setuptools import setup

setup(
    name='ClipCloud',
    version='0.1',
    url='https://github.com/lavelle/ClipCloud',

    author='Giles Lavelle',
    author_email='giles.lavelle@gmail.com',

    description='Two-step sharing for every kind of data',
    long_description=open(os.path.join(os.path.dirname(__file__), 'readme.md')).read(),

    install_requires=[
        'dropbox'
    ],
    py_modules=['src/clipcloud'],
    entry_points={
        'console_scripts': ['clipcloud=clipcloud:main']
    }
)