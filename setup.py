#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    'docker-py', 'docker-map>=0.3', 'fabric', 'docker-fabric'
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='continuity',
    version='0.1.0',
    description="Continuity is a set of tools to help continuous integration using Fabric and Docker.",
    long_description=readme + '\n\n' + history,
    author="Simon Castillo",
    author_email='scastb@gmail.com',
    url='https://github.com/scast/continuity',
    packages=[
        'continuity',
    ],
    package_dir={'continuity':
                 'continuity'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='continuity',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
