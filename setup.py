#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  8 21:26:07 2016

@author: martin
"""
from distutils.core import setup

setup(name='Financial_Life',
      version='0.8',
      description='A framework for analysing financial products in personalized contexts',
      author='Martin Pyka',
      author_email='martin.pyka@gmail.com',
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
      			'financial_life.templates.html.standard'],
      package_data={'financial_life': ['templates/html/standard/*.html']}
     )
