# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('LICENSE') as f:
    license = f.read()

import sys
if sys.version_info < (3, 0):
    py2_requirements = ["unicodecsv"]
else:
    py2_requirements = []
    
setup(
    name='microportraits',
    version='0.1.0',
    description='Extracting micro-portraits',
    author='Antske Fokkens',
    author_email='antske.fokkens@vu.nl',
    url='https://github.com/antske/micro-portraits/',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires = py2_requirements + [
        "KafNafParserPy",
    ]
)

