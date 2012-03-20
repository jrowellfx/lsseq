#!/usr/bin/env python

from distutils.core import setup

setup(name='lsseq',
      version='1.5',
      description='very ls-like image sequence listing command with supporting module',
      author='James Philip Rowell',
      author_email='james@oic-inc.net',
      url='http://www.orangeimagination.com/',
      py_modules=['seqLister'],
      scripts=['lsseq'],
     )
