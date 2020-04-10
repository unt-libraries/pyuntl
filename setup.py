#!/usr/bin/env python

from setuptools import setup


setup(
    name='pyuntl',
    version='2.0.0',
    author='Mark Phillips',
    author_email='mark.phillips@unt.edu',
    url='https://github.com/unt-libraries/pyuntl',
    license='BSD',
    packages=['pyuntl'],
    install_requires=[
        'lxml>=3.4.4',
        'rdflib>=4.2.1',
    ],
    description='read, write and modify UNTL metadata records',
    long_description='See the home page for more information.',
    classifiers=[
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords=['untl', 'metadata', 'digital libraries', 'records'],
    test_suite='tests'
)
