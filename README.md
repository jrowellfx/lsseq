# About lsseq

`lsseq` is a unix/linux command-line utility that
lists directory contents (akin to `/bin/ls`) while condensing image
sequences (or cache sequences) to one entry each and listing the sequence in
a helpful way. Filenames that are part of sequences are assumed to be of
the form:
```
    <descriptiveName>.<frameNum>.<imgExtension>
```
where `<imgExtension>` is drawn from a default list of image extensions or an
environment variable that can be set to override the default list. (see
`lsseq --help` and in particular `--imgExt`).
Note that `lsseq` can also handle the case that the dot-separator
between the `<descriptiveName>` and the `<frameNum>` is an underscore
(see `lsseq --help` for `--looseNumSeparator, -l`).

`lsseq` can print the image sequence in a variety of formats useful for `nuke`,
`houdini` or `rv` and can also print a `glob` pattern for use in the shell. It also
has it's own native output which is nice to read.

#### For example:
```
$ ls
aaa.097.tif  aaa.098.tif  aaa.100.tif  aaa.101.tif  aaa.102.tif  aaa.103.tif
$ lsseq
aaa.[097-103].tif m:[99]
```
What `lsseq` tells us here is that there is a sequence of tif files named
`aaa` with frames 97 through 103 (three padded) and frame 99 is missing.

`lsseq` was written and designed in a way that hopefully makes it unnecessary
for anyone to feel they have to write such a utility ever again.

To that end `lsseq` is designed to have the flavor of the unix/linux/osx `ls`
command as much as possible. The idea is to make it easier on the user when
switching back and forth between using `lsseq` and regular `ls` so that the
look of the output as well as several command-line-arguments are the same
(where possible and it makes sense).

Furthermore it was written to be as robust as possible. For example, it
handles negative frames properly and has been extensively tested and used at
several production studios. There is a regression test program included with
the source here on github to help test any changes, additions, bug fixes
etc.

Lastly some useful options have been added beyond what `/bin/ls` does that
extend `lsseq's` capability.

#### For example:
```
1$ ls -F
aaa/  bbb/  ccc.0101.exr  nonImage.file

2$ ls *
ccc.0101.exr  nonImage.file

aaa:
aaa.097.tif  aaa.098.tif  aaa.100.tif  aaa.101.tif  aaa.102.tif  aaa.103.tif  nonImage_A.file

bbb:
bbx.0097.tif  bbx.0100.tif  bbx.0103.tif  bby.0199.tif  bby.0202.tif      nonImage_B2.file
bbx.0098.tif  bbx.0101.tif  bby.0197.tif  bby.0200.tif  bby.0203.tif
bbx.0099.tif  bbx.0102.tif  bby.0198.tif  bby.0201.tif  nonImage_B1.file

3$ lsseq *
nonImage.file
ccc.[0101].exr

aaa:
nonImage_A.file
aaa.[097-103].tif m:[99]

bbb:
nonImage_B1.file  nonImage_B2.file
bbx.[0097-0103].tif
bby.[0197-0203].tif

4$ lsseq --prependPathRel *
ccc.[0101].exr
aaa/aaa.[097-103].tif m:[99]
bbb/bbx.[0097-0103].tif
bbb/bby.[0197-0203].tif

5$ lsseq --prependPathAbs --skipMissing --format rv *
/user/jrowellfx/test/ccc.0101.exr
/user/jrowellfx/test/aaa/aaa.97-103@@@.tif
/user/jrowellfx/test/bbb/bbx.97-103#.tif
/user/jrowellfx/test/bbb/bby.197-203#.tif
```
The first thing to note above is how close `lsseq` is to mimicking `/bin/ls` in
labelling directories and listing directory contents etc. (compare the
output of command 2 to 3). One difference being that `lsseq` first lists all
non-sequence images in a directory exactly as `ls` would list them (minus the
sequences) then lists all the sequences in their condensed form.

Secondly note the two useful options in commands 4 and 5 above,
`--prependPathRel` and `--prependPathAbs` which can be very useful when creating
lists of sequences to pipe into other scripts.

It's recommended to review the capabilities of lsseq in how it can sort
sequences, especially with respect to how it handles sorting by time. See
`lsseq --help` for `--time, -t and --onlyShow` options.

This package also includes two helpful command-line utilities (`expandseq` and `condenseseq`) that
expand and condense lists of frame numbers into a fairly standard format
used by many computer-graphics programs and CG-production studios.

## How to install lsseq, expandseq and condenseseq on your computer

To install these commands on your system follow these steps (you need root
privileges).

1)  First make sure you have python version 3.x (x >= 6) installed on your machine, you can do
    this simply by typing `python3` at the command prompt. If you are told
    `"command not found"`, then you need to download and install it, there are
    many helpful websites to get this going, not the least of which is [Python.org](https://www.python.org/).

2)  Download `lsseq-2.3.2.tar.gz` assuming that the latest version is `2.3.2` (if
    not just grab the latest one), you can find all versions in the `dist` directory of this
    repo: [jrowellfx/lsseq/dist](dist)

3)  Uncompress the file:
    ```
    $ tar -xvzf lsseq-2.3.2.tar.gz
    ```
4)  install the commands and supporting python module:
    ```
    $ cd lsseq-2.3.2
    $ sudo python3 setup.py install
    ```

5)  ...that's it! You should be able to run the commands `lsseq`, `expandseq`
    and `condenseseq` now.

To test `lsseq` properly `cd` into a directory containing frames from an image
sequence then `lsseq` the contents of the directory.

If you don't have one handy you can try this to test it.
```
$ cd ~
$ mkdir tmp
$ cd tmp
$ touch aaa.001.tif aaa.002.tif aaa.003.tif aaa.004.tif aaa.005.tif
$ lsseq
aaa.[001-005].tif z:[1-5]
```
Note the `z:[1-5]` which is telling you that the frames `aaa.[001-005].tif`
have zero length, and if you had generated those with a renderer I'm
guessing you'd need to rerender them.

Type:
```
$ lsseq --help
$ expandseq --help
$ condenseseq --help
```
for much more useful info.

Please contact `j a m e s <at> a l p h a - e l e v e n . c o m` with any bug
reports, suggestions or oodles of praise as the case may be.

If you want everthing in the `lsseq` repo:
```
$ git clone git@github.com:jrowellfx/lsseq.git
```

