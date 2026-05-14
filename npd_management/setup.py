# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from setuptools import setup

name = 'npd_management'

setup(
	name=name,
	version='0.0.1',
	description='NPD Management App for Tecnofood',
	author='Jorge',
	author_email='tecnofoodmx@gmail.com',
	packages=[name],
	zip_safe=False,
	include_package_data=True,
	install_requires=[
		'frappe',
	]
)
