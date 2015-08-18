#!/usr/bin/env python

from setuptools import setup


setup(
    name='pyuntl',
    version='1.0.0',
    author='Mark Phillips',
    author_email='mark.phillips@unt.edu',
    url='https://github.com/unt-libraries/edtf-validate',
    license='BSD',
    packages=['pyuntl'],
    install_requires=[
        'lxml',
        'rdflib'
    ],
    description='read, write and modify UNTL metadata records',
    classifiers=[
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
    keywords=['untl', 'metadata', 'digital libraries', 'records'],
    test_suite='tests'
)
