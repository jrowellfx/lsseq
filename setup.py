#!/usr/bin/env python

from distutils.core import setup

setup(name='lsseq',
      version='1.601',
      description='ls-like command for image frame sequences',
      long_description='lsseq is built to behave very much like ls, but lists image sequences in a condensed manner.  A supporting module is included.',
      author='James Philip Rowell',
      author_email='james@oic-inc.net',
      url='http://www.orangeimagination.com/',
      py_modules=['seqLister'],
      scripts=['lsseq', 'expandseq', 'condenseseq'],
      license = "BSD 3-Clause license",
     )
