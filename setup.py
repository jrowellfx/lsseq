from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name            = 'lsseq',
    version         = '4.0.1',
    description='ls-like command for image-sequences',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url             = 'https://github.com/jrowellfx/lsseq',
    author          = 'James Philip Rowell',
    author_email    = 'james@alpha-eleven.com',
    license         = "BSD-3-Clause",
    license_files = ["LICENSE"],

    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS',
        'Development Status :: 5 - Production/Stable',
    ],

    packages        = ['lsseq'],
    python_requires = '>=3.7, <4',
    install_requires=['seqLister>=1.0.0'],

    entry_points = {
        'console_scripts': [
            'lsseq = lsseq.__main__:main',
        ]
    }
)
