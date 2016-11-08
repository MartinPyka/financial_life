#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  8 21:26:07 2016

@author: martin
"""


from setuptools import setup, find_packages

setup(name='Financial_Life',
      version='0.8',
      description='A framework for analysing financial products in personalized contexts',
      author='Martin Pyka',
      author_email='martin.pyka@gmail.com',
      url='https://github.com/MartinPyka/financial_life',
      packages=find_packages(
        where='.',
        exclude=('build', 'docs')
     )
)