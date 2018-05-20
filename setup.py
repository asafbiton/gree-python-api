#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

version = '0.3.2'

setup(
    name='gree',
    version=version,
    python_requires='>=3',
    author='Asaf Biton',
    author_email='bit.asaf@gmail.com',
    url='http://github.com/xTCx/gree-python-api',
    packages=find_packages(),
    scripts=[],
    install_requires=['pycryptodome>=3.4.11'],
    description='Python API for controlling Gree ACs',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    include_package_data=True,
    zip_safe=False,
)