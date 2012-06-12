#!/usr/bin/env python

from distutils.core import setup
import os
import shutil

createdCondenseseq = False
if not os.path.exists('condenseseq') :
    shutil.copy2('expandseq', 'condenseseq')
    createdCondenseseq = True

setup(name='lsseq',
      version='1.800',
      description='ls-like command for image frame sequences',
      long_description='lsseq is built to behave very much like ls, but lists image sequences in a condensed manner.  A supporting module is included and two other useful command line utilities: expandseq and condenseseq.',
      author='James Philip Rowell',
      author_email='james@oic-inc.net',
      url='http://www.orangeimagination.com/',
      py_modules=['seqLister'],
      scripts=['lsseq', 'expandseq', 'condenseseq'],
      license = "BSD 3-Clause license",
     )

if createdCondenseseq :
    os.remove('condenseseq')
