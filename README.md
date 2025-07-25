# About lsseq

`lsseq` is a `Unix/Linux/MacOS` command-line utility
that lists directory contents like `/bin/ls` with the
difference that `lsseq` condenses image and cache sequences to one entry each.

Filenames that are part of sequences are assumed to be of the form:

```
    <descriptiveName>.<frameNum>.<imgExtension>
```
where `<imgExtension>` is drawn from a comprehensive list of image extensions,
or from a user supplied environment variable.
`lsseq` also handles the case when the separator
between the `<descriptiveName>` and the `<frameNum>` is an underscore instead of a dot.

`lsseq` first lists all non-image-sequence files followed by the
list of image sequences as such:

```
    $ lsseq
    [output of /bin/ls minus image sequences]
    [list of images sequences]
```

#### Example:

```
    $ ls
    aaa.097.tif  aaa.100.tif  aaa.102.tif  bar.pdf
    aaa.098.tif  aaa.101.tif  aaa.103.tif  foo.txt
    $ lsseq
    bar.pdf  foo.txt
    aaa.[097-103].tif m:[99]
```

What `lsseq` tells us here is
that this directory contains two non-image files, `bar.pdf` and `foo.txt`,
plus a sequence of tif files named
`aaa` with frames 97 through 103 (three padded) and frame 99 is missing.

`lsseq` prints sequences in its own native format, which is nice to read,
however it can print sequences in a variety of formats useful for `nuke`,
`houdini` or `rv` as well as a `glob` pattern for use in the shell.

#### Example:

```
    $ ls
    bbb.097.jpg  bbb.099.jpg  bbb.101.jpg  bbb.103.jpg
    bbb.098.jpg  bbb.100.jpg  bbb.102.jpg
    $ lsseq
    bbb.[097-103].jpg
    $ lsseq --format rv
    bbb.97-103@@@.jpg
    $ rv `lsseq -f rv`
    <rv launches with sequence bbb>
    $ lsseq -f nuke
    bbb.%03d.jpg 97-103
    $ lsseq -f glob
    bbb.[0-9][0-9][0-9].jpg
```
## Installing lsseq

```
    python3 -m pip install lsseq --upgrade
```

There is additional installation-information below in an
[addendum](https://github.com/jrowellfx/lsseq#addendum---more-on-installing-command-line-tools)
below with a helpful technique for installing `lsseq` system-wide.

#### Testing installation

To test `lsseq`, `cd` into a directory containing frames from an image
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
have zero length.

## Deeper dive on lsseq capabilities

`lsseq` was written to be as robust as possible. For example, it
handles negative frames properly and has been extensively tested and used at
several production studios for many years.

Furthermore, to ensure that updates to `lsseq` don't
introduce new bugs, the `lsseq` repo contains extensive regression tests that
are run and passed before every new release.

### Why use lsseq?

Anyone who generates or works with frames of images for film and video needs `lsseq`.
If not already using `lsseq`, then all major post-production 
studios have some kind of version of this essential tool.
However
[I](https://github.com/jrowellfx) believe that
`lsseq` is quintessential.

#### lsseq reports useful information in a nice compact form

Even if you aren't an avid command-line user, having `lsseq` available to you might 
make you a convert because it reports VERY useful information about sequences
that are otherwise hard to discover without using `lsseq`.

#### Example:

```
    $ ls
    ccc_v01.0995.exr  ccc_v01.1029.exr  ccc_v02.1019.exr  ccc_v03.1008.exr
    ccc_v01.0996.exr  ccc_v01.1030.exr  ccc_v02.1020.exr  ccc_v03.1009.exr
    ccc_v01.0997.exr  ccc_v01.1031.exr  ccc_v02.1021.exr  ccc_v03.1010.exr
    ccc_v01.0998.exr  ccc_v01.1032.exr  ccc_v02.1022.exr  ccc_v03.1011.exr
    ccc_v01.1000.exr  ccc_v01.1033.exr  ccc_v02.1023.exr  ccc_v03.1012.exr
    ccc_v01.1001.exr  ccc_v01.1034.exr  ccc_v02.1024.exr  ccc_v03.1013.exr
    ccc_v01.1002.exr  ccc_v01.1035.exr  ccc_v02.1025.exr  ccc_v03.1014.exr
    ccc_v01.1003.exr  ccc_v02.0995.exr  ccc_v02.1026.exr  ccc_v03.1015.exr
    ccc_v01.1004.exr  ccc_v02.0996.exr  ccc_v02.1027.exr  ccc_v03.1016.exr
    ccc_v01.1005.exr  ccc_v02.0997.exr  ccc_v02.1028.exr  ccc_v03.1017.exr
    ccc_v01.1006.exr  ccc_v02.0998.exr  ccc_v02.1029.exr  ccc_v03.1018.exr
    ccc_v01.1007.exr  ccc_v02.0999.exr  ccc_v02.1030.exr  ccc_v03.1019.exr
    ccc_v01.1008.exr  ccc_v02.1000.exr  ccc_v02.1031.exr  ccc_v03.1020.exr
    ccc_v01.1009.exr  ccc_v02.1001.exr  ccc_v02.1032.exr  ccc_v03.1021.exr
    ccc_v01.1010.exr  ccc_v02.1002.exr  ccc_v02.1033.exr  ccc_v03.1022.exr
    ccc_v01.1011.exr  ccc_v02.1003.exr  ccc_v02.1034.exr  ccc_v03.1023.exr
    ccc_v01.1012.exr  ccc_v02.1004.exr  ccc_v02.1035.exr  ccc_v03.1024.exr
    ccc_v01.1013.exr  ccc_v02.1005.exr  ccc_v03.0995.exr  ccc_v03.1025.exr
    ccc_v01.1014.exr  ccc_v02.1006.exr  ccc_v03.0996.exr  ccc_v03.1026.exr
    ccc_v01.1015.exr  ccc_v02.1007.exr  ccc_v03.0997.exr  ccc_v03.1027.exr
    ccc_v01.1016.exr  ccc_v02.1008.exr  ccc_v03.0998.exr  ccc_v03.1028.exr
    ccc_v01.1017.exr  ccc_v02.1009.exr  ccc_v03.0999.exr  ccc_v03.1029.exr
    ccc_v01.1018.exr  ccc_v02.1010.exr  ccc_v03.1000.exr  ccc_v03.1030.exr
    ccc_v01.1019.exr  ccc_v02.1011.exr  ccc_v03.1001.exr  ccc_v03.1031.exr
    ccc_v01.1020.exr  ccc_v02.1012.exr  ccc_v03.1002.exr  ccc_v03.1032.exr
    ccc_v01.1021.exr  ccc_v02.1013.exr  ccc_v03.1003.exr  ccc_v03.1033.exr
    ccc_v01.1025.exr  ccc_v02.1014.exr  ccc_v03.1004.exr  ccc_v03.1034.exr
    ccc_v01.1026.exr  ccc_v02.1015.exr  ccc_v03.1005.exr  ccc_v03.1035.exr
    ccc_v01.1027.exr  ccc_v02.1016.exr  ccc_v03.1006.exr
    ccc_v01.1028.exr  ccc_v02.1018.exr  ccc_v03.1007.exr

    $ lsseq
    ccc_v01.[0995-1035].exr m:[999,1022-1024], z:[1030-1033]
    ccc_v02.[0995-1035].exr m:[1017]
    ccc_v03.[0995-1035].exr
```

This is a typical example of how hard it is to look at the contents of a directory
containing image sequences without `lsseq`.

It's tough to spot that frames
`999` and `1022-1024` are missing from `v01` of the sequence,
and frame `1017` is missing from `v02`.
Furthermore, without doing a long listing (i.e. "`ls -l`"),
you might miss that frames `1030-1033` of `v01` 
are also zero length and empty. Maybe a bad render?

As you can see above, that information easily pops out when using `lsseq`.

If you like, you can turn off reporting zero-length and missing frames with some
command-line options:

```
    $ lsseq --skip-missing --skip-zero
    ccc_v01.[0995-1035].exr
    ccc_v02.[0995-1035].exr
    ccc_v03.[0995-1035].exr
```

#### lsseq is a natural partner to /bin/ls

`lsseq` is designed to have the flavor of the Unix/Linux/MacOS `ls`
command as much as possible. The idea is to make it easier on the user when
switching back and forth between using `lsseq` and regular `ls` so that the
look of the output as well as several command-line-arguments are the same
(where possible and makes sense).

The following example shows the similarity between the two commands.
Command #1 and #2 below call `/bin/ls` on a sample directory.
Then command #3 calls `lsseq` with the same wildcard as #2:

```
    1$ ls -F
    aaa/  bbb/  ccc.0101.exr  nonImage.file

    2$ ls *
    ccc.0101.exr  nonImage.file

    aaa:
    aaa.097.tif  aaa.100.tif  aaa.102.tif  nonImage_A.file
    aaa.098.tif  aaa.101.tif  aaa.103.tif

    bbb:
    bbx.0097.tif  bbx.0101.tif  bby.0198.tif  bby.0202.tif
    bbx.0098.tif  bbx.0102.tif  bby.0199.tif  bby.0203.tif
    bbx.0099.tif  bbx.0103.tif  bby.0200.tif  nonImage_B1.file
    bbx.0100.tif  bby.0197.tif  bby.0201.tif  nonImage_B2.file

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
```

The first thing to note above is how close `lsseq` is to mimicking `/bin/ls` in
labelling directories and listing directory contents etc. (compare the
output of command #2 to #3). The difference being that `lsseq` first lists all
non-sequence images in a directory exactly as `ls` would list them (minus the
sequences) then lists all the sequences in their condensed form.

#### Natural extension of lsseq beyond /bin/ls

Some useful options have been added, beyond what `/bin/ls` does, that
extend `lsseq's` capability.

```
    4$ lsseq --prepend-path-rel *
    ccc.[0101].exr
    aaa/aaa.[097-103].tif m:[99]
    bbb/bbx.[0097-0103].tif
    bbb/bby.[0197-0203].tif

    5$ lsseq --prepend-path-abs --skip-missing --format rv *
    /user/jrowellfx/test/ccc.0101.exr
    /user/jrowellfx/test/aaa/aaa.97-103@@@.tif
    /user/jrowellfx/test/bbb/bbx.97-103#.tif
    /user/jrowellfx/test/bbb/bby.197-203#.tif
```

Continuing in our sample directory from the previous example,
note the two options in commands #4 and #5, namely
`--prepend-path-rel` and `--prepend-path-abs`. These are both useful when creating
lists of sequences to pipe into other scripts.

#### Sorting by modification times

`/bin/ls` allows us to sort directory contents by modification time as well as
by filename. `lsseq` also duplicates this functionality but adds options to specify
which frame from each sequence to use when comparing modification times. You can
compare sequences by comparing the `oldest`, `median` or `newest` frames from
each sequence with the `--time FRAME_AGE` option.

`lsseq` can also limit listing sequences that are created before
or after a given timestamp with the `--only-show TENSE [CC]YYMMDD[-hh[mm[ss]]]` option,
where `TENSE` is either `before` or `since`.

An especially powerful feature of `lsseq` is the ability to sort by time
across different directories. This is special to `lsseq` as `/bin/ls` doesn't 
sort by time across directories. Here's how you do it with `lsseq`, the
description snipped from the output of `lsseq --help`:

```
  --global-sort-by-time  when using either --prepend-path-abs or --prepend-path-rel
                         then this option will sort ALL sequences by time
                         compared to each other, as opposed to only sorting
                         sequences by time within their common directory. If
                         the above conditions are NOT met, then this option is
                         simply ignored.
```

Please explore the rest of `lsseq's` capabilities by typing:

```
    $ lsseq --help
```

#### Error codes returned by `lsseq`

As copied from the source code,
the following EXIT codes will be combined bitwise to return
possibly more than one different warning and/or error.

```
EXIT_NO_ERROR               = 0 # Clean exit.
EXIT_LS_ERROR               = 1 # A call to 'ls' returned an error code.
EXIT_ARGPARSE_ERROR         = 2 # A bad option was passed to lsseq. Exit lsseq.
EXIT_LSSEQ_SOFTLINK_WARNING = 4 # warning - broken softlink found
EXIT_LSSEQ_PADDING_WARNING  = 8 # warning - two images with same name, same frame-num, but diff padding
EXIT_CD_PERMISSION_WARNING  = 16 # warning - recursive descent blocked - no execute permission on dir
```

## `lsseq --help`
A full listing of all the command-line options follows, as displayed when running `lsseq --help`.

```
usage: lsseq [-h | --help] [OPTION]... [FILE]...

List directory contents like /bin/ls except condense image
sequences to one entry each. Filenames that are part of image
sequences are assumed to be of the form:

    <descriptiveName>.<frameNum>.<imgExtension>

where <imgExtension> is drawn from a default list of image extensions
(displayed with option --img-ext) or alternatively from the environment
variable LSSEQ_IMAGE_EXTENSION which should contain a colon separated
list of image file extensions.

lsseq first lists all non-image-sequence files followed by the
list of image sequences as such:

    $ lsseq
    [output of /bin/ls minus image sequences]
    [list of images sequences]

positional arguments:
  FILE                  file names

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --format FORMAT, -f FORMAT
                        list image sequences in various formats. The choices
                        are 'native' (default), 'nuke', 'rv', 'shake', 'glob',
                        'mplay', and 'houdini'. Note that glob prints correct
                        results only if the frame numbers are padded. Further
                        note that reporting of missing/bad/etc frames (e.g.
                        --show-missing) only happens with 'native' format
  --show-missing, -m    show list of missing frames as 'm:[<list>]' [default]
  --skip-missing, -M    do not show list of missing frames
  --show-zero, -z       show list of zero length images as 'z:[<list>]'
                        [default]
  --skip-zero, -Z       do not show list of zero length images
  --show-bad-frames, -b
                        lists potentially bad frames based on the minimum size
                        of a good frame (see --good-frame-min-size). Reported
                        as 'b:[<list>]'
  --skip-bad-frames, -B
                        do not show list of potentially bad frames [default]
  --good-frame-min-size BYTES
                        any frame size less than BYTES is a bad frame. Short
                        forms for byte sizes are accepted as in '1K' (i.e.,
                        1024) or '1.5K' for example. [default: 512]
  --show-bad-padding    report badly padded frame numbers which occurs when a
                        number is padded but shouldn't be, or isn't padded but
                        it should be. Reported as 'p:[<list>]' [default]
  --skip-bad-padding    do not show list of badly padded frames
  --combine-lists, -c   combine the lists of zero, missing and bad frames into
                        one list. Reported as 'e:[<list>]'
  --no-combine-lists    Don't combine the error lists
  --no-error-lists, -n  Skip printing ALL error lists. Note: Setting --show-
                        bad-padding (for example) AFTER this option on the
                        command line has the effect of ONLY showing the bad-
                        padding error list
  --split-sequence      prints sequences with missing frames as separate
                        sequences as if there are multiple sequences with the
                        same name, but with different frame ranges. Note: this
                        option only affects the printing of a sequence, not in
                        how sequence times are calculated. In other words,
                        sorting by time might not produce the results you
                        would expect when splitting sequences with this
                        option.
  --no-split-sequence   consider frames with the same name as all being part
                        of the same sequence. [default]
  --loose-num-separator, -l
                        allow the use of '_' (underscore), in addition to '.'
                        (dot) as a separator between the descriptiveName and
                        frameNumber when looking to interpret filenames as
                        image sequences. i.e.,
                        <descriptiveName>_<frameNum>.<imgExtension> (also see
                        --strict-num-separator)
  --strict-num-separator, -s
                        strictly enforce the use of '.' (dot) as a separator
                        between the descriptiveName and frameNumber when
                        looking to interpret filenames as image sequences.
                        i.e., <descriptiveName>.<frameNum>.<imgExtension>
                        (also see --loose-num-separator) [default]
  --only-sequences, -o  only list image sequences, cache sequences and movies
  --only-images, -O     strictly list only image sequences (i.e., no movies or
                        caches)
  --only-movies         strictly list only movies (i.e., no images or caches)
  --only-caches         strictly list only cache sequences (i.e., no images or
                        movies)
  --img-ext, -i         print list of image, cache and movie file extensions
                        and exit
  --prepend-path-abs, -p
                        prepend the absolute path name to the image name. This
                        option implies the option --only-sequences and also
                        suppresses printing directory name headers when
                        listing directory contents
  --prepend-path-rel, -P
                        prepend the relative path name to the image name. This
                        option implies the option --only-sequences and will
                        also suppress printing directory name headers when
                        listing directory contents
  --extremes, -e        only list the first and last image on a separate line
                        each. This option implies --prepend-path-abs (unless
                        --prepend-path-rel is explicitly specified) and
                        --only-sequences
  --single, -1          list one non-sequence entry per line (see ls(1))
  --all, -a             do not ignore entries starting with '.' while omitting
                        implied '.' and '..' directories (see ls(1) --almost-
                        all)
  --by-columns, -C      list non-sequence entries by columns (see ls(1))
  --by-rows, -x         list non-sequence entries by lines instead of by
                        columns (see ls(1))
  --directory, -d       list directory entries instead of contents, and do not
                        dereference symbolic links (see ls(1))
  --classify, -F        append indicator (one of */=>@|) to entries (see
                        ls(1))
  --reverse, -r         reverse order while sorting
  --recursive, -R       list subdirectories recursively
  --sort-by-time, -t    sort by modification time, the default comparison time
                        is between the most recently modified (newest) frames
                        in each sequence. (see --time) (see ls(1))
  --time FRAME_AGE      which frame in the sequence to use to compare times
                        between sequences when sorting by time. The possible
                        values for 'FRAME_AGE' are 'oldest', 'median' and
                        'newest' [default: 'newest']
  --only-show TENSE [CC]YYMMDD[-hh[mm[ss]]]
                        where TENSE is either 'before' or 'since'; only list
                        sequences up to (and including) or after (and
                        including) the time specified. The --time argument
                        specifies which frame to use for the cutoff
                        comparison. The optional CC (century) defaults to the
                        current century. The optional '-hh' (hours), 'mm'
                        (minutes) or 'ss' (seconds) default to zero if not
                        specified.
  --global-sort-by-time, -G
                        when using either --prepend-path-abs or --prepend-
                        path-rel then this option will sort ALL sequences by
                        time compared to each other, as opposed to only
                        sorting sequences by time within their common
                        directory. If the above conditions are NOT met, then
                        this option is simply ignored.
  --silent, --quiet     suppress error and warning messages
```

## Addendum - more on installing command-line tools

Here's the process that I've followed to install `lsseq`, as well as my other
python-based command-line
tools (i.e., [`renumseq`](https://github.com/jrowellfx/renumSeq), [`expandseq`](https://github.com/jrowellfx/expandseq), [`condenseseq`](https://github.com/jrowellfx/expandseq) and [`fixSeqPadding`](https://github.com/jrowellfx/fixSeqPadding))
so that they are accessible to all users. This works on both MacOS and Linux.

```
    $ su -
    # cd /usr/local
    # python3 -m venv venv
    # cd venv
    # source bin/activate
    # python3 -m pip install --upgrade pip
    # deactivate
    # bin/pip install lsseq --upgrade
    # bin/pip install expandSeq --upgrade
    # bin/pip install renumSeq --upgrade
    # bin/pip install fixSeqPadding --upgrade
    # ln -s /usr/local/venv/bin/lsseq /usr/local/bin/lsseq
    # ln -s /usr/local/venv/bin/expandseq /usr/local/bin/expandseq
    # ln -s /usr/local/venv/bin/condenseseq /usr/local/bin/condenseseq
    # ln -s /usr/local/venv/bin/renumseq /usr/local/bin/renumseq
    # ln -s /usr/local/venv/bin/fixseqpadding /usr/local/bin/fixseqpadding
    # exit
    $ lsseq --version
    4.1.0
```

At this point any user should be able to run any of the commands linked in the example above.
Note that updates are easy now too. Say there's an update to lsseq that you want to install.

```
    $ su -
    # cd /usr/local/venv
    # bin/pip install lsseq --upgrade
    # exit
    $ lsseq --version
    99.99.99
```

Just kidding about the version number, maybe in the year 2159? Will Unix still be a thing!?

### Helpful hint: Upgraded the system-wide default version of python3?

Say you had installed `lsseq` as described above, while the default `python3` was linked to `python3.6`.
Then suppose the system default `python3` was then linked to a higher version of python
(Check with: `python3 --version`).
At that point running `lsseq` might error out like this:

```
Traceback (most recent call last):
  File "/usr/local/bin/lsseq", line 5, in <module>
    from lsseq.__main__ import main
ModuleNotFoundError: No module named 'lsseq'
```
This is an easy problem to fix. Delete (or move to a backup location)
the entire directory `/usr/local/venv` and redo the steps above
to install lsseq, renumseq, expandseq etc. from scratch.

# Important: latest MAJOR point release of `lsseq`.

`lsseq` and all the utilities provided by jrowellfx github repos
use "[`Semantic Versioning 2.0.0`](https://semver.org/)" in numbering releases.
The latest release of `lsseq` upped the `MAJOR` release number
from `v3.x.x` to `v4.x.x`.

While the functionality and output of `lsseq` has not changed, all the so called
"long options" have been renamed to adhere to `POSIX` standard naming
conventions.

That is, prior to `v4.0.0` of `lsseq` all the long-option names used a "camel case"
naming convention but as of `v4.0.0` all long-option names have been
changed to so-called "kebab case".

For example:

```
--globalSortByTime
```

has been changed to

```
--global-sort-by-time
```

In the event that you have written any scripts that make use of `lsseq` or
any other of `jrowellfx`'s utils provided [here](https://github.com/jrowellfx) 
you will need to edit your scripts to be able to update to the lastest versions
of the utilities.

In this case, in order to assist in switching to the
current `MAJOR` point release some `sed` scripts have been provided that should make
the transition quite painless. Especially if you make use
of [`runsed`](https://github.com/jrowellfx/vfxTdUtils) which if you haven't used it before,
now is the time, it's extremely helpful.

There are two files provided at the root-level of the repo, namely:
`sed.script.jrowellfx.doubleDashToKebab` and `sed.script.lsseq.v3tov4`.

The first one can be used to fix the long-option names for ALL the 
`MAJOR` point release updates to the long-options in any of `jrowellfx`'s utilities.
The second one contains only changes needed for the updates to `lsseq`.

## Example `sed.script` usage.

Download one or both of the sed scripts named above. Make sure you have `runsed` installed
on your system.

```
$ cd ~/bin
$ ls
myScriptThatUsesLsseq
$ cat myScriptThatUsesLsseq
#!/bin/bash

lsseq --globalSortByTime --recursive --prependPathAbs /Volumes/myProjectFiles

$ mv ~/Downloads/sed.script.jrowellfx.doubleDashToKebab sed.script
$ runsed myScriptThatUsesLsseq
$ ./.runsed.diff.runsed
+ /usr/bin/diff ./.myScriptThatUsesLsseq.runsed myScriptThatUsesLsseq
3c3
< lsseq --globalSortByTime --recursive --prependPathAbs /Volumes/myProjectFiles
---
> lsseq --global-sort-by-time --recursive --prepend-path-abs /Volumes/myProjectFiles
$ cat myScriptThatUsesLsseq
#!/bin/bash

lsseq --global-sort-by-time --recursive --prepend-path-abs /Volumes/myProjectFiles
```

Note that if you are unhappy with the changes you can undo them easily with

```
$ ./.runsed.undo.runsed
$ cat myScriptThatUsesLsseq
#!/bin/bash

lsseq --globalSortByTime --recursive --prependPathAbs /Volumes/myProjectFiles


```

## Contact

Please contact `j a m e s <at> a l p h a - e l e v e n . c o m` with any bug
reports, suggestions or praise as the case may be.
