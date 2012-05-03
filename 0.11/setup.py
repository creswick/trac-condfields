#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

from setuptools import setup

setup(
    name = 'TracCondFields',
    version = '2.0',
    packages = ['condfields'],
    package_data = { 'condfields': ['templates/*', 'htdocs/*.js', 'htdocs/*.css' ] },

    author = 'Noah Kantrowitz',
    author_email = 'noah@coderanger.net',
    description = 'Support for conditional fields in different ticket types.',
    license = 'BSD',
    keywords = 'trac plugin ticket conditional fields',
    url = 'http://trac-hacks.org/wiki/CondFieldsPlugin',
    classifiers = [
        'Framework :: Trac',
    ],
    
    install_requires = ['Trac>=0.11'],

    entry_points = {
        'trac.plugins': [
            'condfields.web_ui = condfields.web_ui',
        ]
    },
)
