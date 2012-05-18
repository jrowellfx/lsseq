.ll 76
.na
.hy 0
.pl 1
How to install lsseq, expandseq and condenseseq on your computer.

lsseq, expandseq and condenseseq are three command line utilities
to help you deal with sequences of images.

lsseq is designed to have the flavor and some of the power of the
unix/linux/osx "ls" program.
The idea is to make it easier on the user when
switching back and forth between using "lsseq" and regular "ls" so
that the look of the output as well as several
command-line-arguments are the same (where possible and
it makes sense).

There are also two utilities that expand and condense lists of frame numbers into
a fairly standard format used by many computer-graphics programs and 
CG-production studios.

To install these commands on your system follow these steps (you need 
root privileges).

First make sure you have python installed on your machine, you 
can do this simply by typing "python --version" at the command prompt.
If you are told "command not found",
then you need to download and install python.  Version 2.6
or 2.7 are probably best - this hasn't been tested on vers 3.0.

.in +3
.ti -3
1) If you are running python version 2.7+ then skip to step 2.

You need to install the python module argparse (if not already installed)
since it is becoming a standard part of python starting in 2.7,
but it works well in 2.3+, you just have to install it manually.

This is a simple task:
.in +2
.ti -2
- Go to http://pypi.python.org/pypi/argparse
.ti -2
- Scroll down and find the "Download URL" link (it will be a *.tar.gz file).
.ti -2
- Download the file then type (for example):
.nf
$ tar -xvf argparse-1.2.1.tar.gz
$ cd argparse-1.2.1
$ sudo python setup.py install
.fi
.in -2

.ti -3
2) Download lsseq-1.700.tar.gz
assuming that the latest version is 1.700 (if not
just grab the latest one).

.ti -3
3) Uncompress the file:
.nf
$ tar -xvf lsseq-1.700.tar.gz
.fi

.ti -3
4) install the commands and supporting python module:
.nf
$ cd lsseq-1.700
$ sudo python setup.py install
.fi

.ti -3
4) ...that's it! You should be able to run the commands "lsseq", "expandseq"
and "condenseseq" now.
.in -3

To test lsseq properly cd into a directory containing frames from an 
image sequence then "lsseq" the contents of the directory.

If you don't have one handy you can try this to test it.

.nf
$ cd ~
$ mkdir tmp
$ cd tmp
$ touch aaa.001.tif aaa.002.tif aaa.003.tif aaa.004.tif aaa.005.tif
$ lsseq 
aaa.[001-005].tif z:[1-5]
.fi

Note the "z:[1-5]" which is telling you that the frames aaa.[001-005].tif
have zero length, and if you had generated those with a renderer I'm guessing
you'd need to rerender them.  Handy eh!?

Type:

.nf
$ lsseq --help
$ expandseq --help
$ condenseseq --help
.fi

for much more useful info.

Please contact j a m e s <at> o i c - i n c . n e t with any bug reports, suggestions
or oodles of praise as the case may be.

Also, the repos for this project, and some test code etc. is on github, which
you can get here:
.nf
$ cd ~
$ git clone git@github.com:jrowellfx/lsseq.git

