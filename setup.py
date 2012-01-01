#!/usr/bin/env python
# encoding: utf-8
from setuptools import setup
from wsgid import __progname__, __version__, __description__
import os
import sys

setup(
  name=__progname__,
  version=__version__,
  url="https://github.com/daltonmatos/wsgid",
  license="3-BSD",
  description=__description__,
  author="Dalton Barreto",
  author_email="daltonmatos@gmail.com",
  long_description=open('README.rst').read(),
  packages=['wsgid', 'wsgid/core', 'wsgid/commands', 'wsgid.loaders'],
  scripts=['scripts/wsgid'],
  install_requires = ['plugnplay==0.2', 'pyzmq==2.1.10', 'python-daemon==1.6', 'simplejson==2.3.0', 'argparse==1.2.1'],
  classifiers = [
    "License :: OSI Approved :: BSD License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Topic :: Software Development :: Libraries :: Application Frameworks"
    ])

