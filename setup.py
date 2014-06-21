#!/usr/bin/env python

from distutils.core import setup

setup(
    name='pv',
    version='0.2',
    description='PV Inverter Monitoring Library',
    author='Edmund Tse',
    author_email='tseedmund@gmail.com',
    url='http://pv.codeplex.com/',
    py_modules=['pv.pvoutput', 'pv.cms'],
)
