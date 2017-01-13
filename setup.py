#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  8 21:26:07 2016

@author: martin
"""
try:
    from setuptools import setup
    have_setuptools = True
except ImportError:
    from distutils.core import setup
    have_setuptools = False

skw = dict(
    name='financial_life',
    version='0.9.3',
    description='A framework for analysing financial products in personalized contexts',
    author='Martin Pyka',
    author_email='martin.pyka@gmail.com',
    maintainer='Martin Pyka',
    maintainer_email='martin.pyka@gmail.com',
    url='https://github.com/MartinPyka/financial_life',
    keywords=["finance", "analysis", "simulation", "loan", "bank"],
    license="Apache License, Version 2.0",
    packages=['financial_life',
              'financial_life.calendar_help',
      	 	  'financial_life.examples',
      	 	  'financial_life.financing',
              'financial_life.products.germany.lbs',
              'financial_life.reports',
              'financial_life.tax.germany',
              'financial_life.templates.html.standard',
    ],
    package_data={'financial_life': ['templates/html/standard/*.html']}
)

if have_setuptools is True:
	skw['install_requires'] = [
		'Jinja2>=2.7.2,<3',
		'matplotlib>=1.3.1,<2',
		'numpy>=1.8.1,<2',
		'pandas>=0.18.1,<1',
		'tabulate>=0.7.5,<1',
	]

setup(**skw)
