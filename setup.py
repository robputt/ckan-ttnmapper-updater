# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages
import os

base_name='ckan_ttnmapper_updater'

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name=base_name,
    version='1.0',
    author=u'Robert Putt',
    author_email='rob@puttfamily.co.uk',
    include_package_data = True,
    packages=find_packages(), # include all packages under this directory
    description='to update',
    long_description="",
    zip_safe=False,

    entry_points = {'console_scripts':
                     ['ckan_ttnmapper_updater = ckan_ttnmapper_updater:run_updater'],
                    },

    # Adds dependencies
    install_requires = ['requests',
                        'requests-toolbelt'
                        ]
)
