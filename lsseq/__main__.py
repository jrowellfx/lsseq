#!/usr/bin/env python3

# 3-Clause BSD License
# 
# Copyright (c) 2008-2022, James Philip Rowell,
# Alpha Eleven Incorporated
# www.alpha-eleven.com
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
#  1. Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
# 
#  2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
# 
#  3. Neither the name of the copyright holder, "Alpha Eleven, Inc.",
#     nor the names of its contributors may be used to endorse or
#     promote products derived from this software without specific prior
#     written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# NOTE: previously the copyright was under my name plus my
# old-company's name. That is,
#
# Copyright (c) 2008-2012, James Philip Rowell,
# Orange Imagination & Concepts, Inc.
# www.orangeimagination.com
# All rights reserved.
#
# etc. <snip>
#
# which explains the use of the "OIC" prefix for my env-variables below.
#     NOTE: the OIC env vars are being phased out in favor of LSSEQ prefix.

# lsseq - List directory contents while condensing images sequences to
# one entry each.  Filenames that are part of images sequences are
# assumed to be of the form:
#     <descriptiveName>.<frameNum>.<imgExtension>

import argparse
import os
import sys
import subprocess
import textwrap
import math
import copy
import shutil
from operator import itemgetter
import seqLister

# MAJOR version for incompatible API changes
# MINOR version for added functionality in a backwards compatible manner
# PATCH version for backwards compatible bug fixes
#
VERSION = "3.0.1"     # Semantic Versioning 2.0.0

PROG_NAME = "lsseq"

gCacheExtList = [
    "ass",
    "bgeo",
    "bgeo.gz",
    "bgeo.sc",
    "dshd",
    "fur",
    "ifd",
    "ifd.gz",
    "ifd.sc",
    "obj",
    "srf",
    "tx",
    "vdb",
    "vdb.gz",
    "vdb.sc"
]
gMovieExtList = [
    "avi",
    "mov",
    "mp4",
    "mpg",
    "mxf",
    "wmv"
]
gImageExtList = [
    "alpha",
    "als",
    "anim",
    "ari",
    "arw",
    "avif",
    "bmp",
    "btf",
    "bw",
    "cin",
    "cr2",
    "crw",
    "dib",
    "dng",
    "dpx",
    "exr",
    "gfa",
    "gif",
    "giff",
    "heic",
    "heif",
    "icon",
    "iff",
    "img",
    "int",
    "inta",
    "jpe",
    "jpeg",
    "jpg",
    "mask",
    "matte",
    "nef",
    "orf",
    "pct",
    "pct1",
    "pct2",
    "pdb",
    "pdd",
    "pef",
    "pic",
    "piclc",
    "picnc",
    "pict",
    "pix",
    "png",
    "psb",
    "psd",
    "ptx",
    "raf",
    "rat",
    "raw",
    "rdc",
    "rgb",
    "rgba",
    "rle",
    "rmf",
    "rw2",
    "sgi",
    "tga",
    "tif",
    "tiff",
    "tpic"
]

# List of date formats accepted to set file times with --onlyShow.
#
# Note: We MUST list %y before %Y in each case below to make sure
# that, for example, "200731" get's interpreted as July 31, 2020
# and not March 1, 2007, as it will if %Y is listed first because
# strptime() does not enforce zero padding for month, day, etc.
#
# Note the ordered pairs below. The second entry is the length
# of a properly zero padded date string, used to double check
# any matches that strptime() makes.
#
DATE_FORMAT_LIST = [
    ('%y%m%d', 6),
    ('%Y%m%d', 8),
    ('%y%m%d-%H', 9),
    ('%Y%m%d-%H', 11),
    ('%y%m%d-%H%M', 11),
    ('%Y%m%d-%H%M', 13),
    ('%y%m%d-%H%M%S', 13),
    ('%Y%m%d-%H%M%S', 15),
    ('%y%m%d%H%M', 10),    # Undocumented, but kept for compatibility
    ('%Y%m%d%H%M', 12),    # with earlier versions (v2.5.3 and earlier)
    ('%y%m%d%H%M.%S', 13), # of lsseq. Note MMDDhhmm[.ss] is no longer
    ('%Y%m%d%H%M.%S', 15)  # supported, thus not FULLY backward compatible.
]

# Support for --globalSortByTime feature.
#
gTimeList = []
gImageDictionary = {}
gCacheDictionary = {}
gMoviesDictionary = {}

# EXIT codes, they will be combined bitwise to return 
# possibly more than one different warning and/or error.
#
EXIT_NO_ERROR               = 0 # Clean exit.
EXIT_LS_ERROR               = 1 # A call to 'ls' returned an error or another internal issue
EXIT_ARGPARSE_ERROR         = 2 # The default code that argparse exits with if bad option.
EXIT_LSSEQ_SOFTLINK_WARNING = 4 # warning - broken softlink
EXIT_LSSEQ_PADDING_WARNING  = 8 # warning - two images with same name, same frame-num, diff padding
#
gExitStatus = EXIT_NO_ERROR

# Array indices for timeList (used in "listSeqDir()") and gTimeList
#
DICTKEY = 0
MTIME = 1
TRAVERSEDPATH = 2

PATH_NOPREFIX = 0
PATH_ABS = 1
PATH_REL = 2

LIST_ALLFILES   = 0
LIST_ONLYSEQS   = 1 # Images, movies and caches.
LIST_ONLYIMGS   = 2 # Strictly images.
LIST_ONLYMOVS   = 3 # Strictly movies.
LIST_ONLYCACHES = 4 # Strictly caches.

BY_UNSPECIFIED = 0
BY_SINGLE = 1
BY_COLUMNS = 2
BY_ROWS = 3

# Array indices for the data list within the image dictionary.
#
FRAME_NUM = 0
FRAME_SIZE = 1
FRAME_MTIME = 2
FRAME_PADDING = 3

FRAME_BROKENLINK = -1

# Array indices for results of the "seqSplit()" function.
#
SEQKEY = 0
FRAMENUM = 1

# Given that we are not allowing "no separator" between the
# descriptive filename and the frame number, then the only
# other character besides "." (dot) that makes sense to have as a
# separator is "_" (underscore).
#
# Clearly we should not allow alphanumeric characters as separators,
# NOR unix/linux/windows shell special characters NOR minus ("-")
# NOR space (" ").  That potentially leaves us with only "_", "+",
# "^" and "~".  Tilde has associations with tmp/crufty files or user
# home directories and his unlikely to ever be used as a separator
# character.  "+" and "^" are potentially usable in as separators
# but unlikely to be used so the effort to generalize the mechanism
# to support the "loose" separator to a list is not worth the effort.
# Thus "loose" is only defined as the use of "_" over and above the
# far more desirable strict case of only allowing ".".
#
# Actually the following global variable is never used in the code.
# But keeping it here for the important discussion above.
#
LOOSE_SEP = "_"

def isFrameNum(f) :
    return (f != '') and (f.isdigit() or (f[0] == '-' and f[1:].isdigit()))

def readByteShortForm(numBytes) :
    multiplier = 1
    if numBytes[-1] == 'K' or numBytes[-1] == 'k' :
        multiplier = 1<<10
        numBytes = numBytes[:-1]
    elif numBytes[-1] == 'M' or numBytes[-1] == 'm' :
        multiplier = 1<<20
        numBytes = numBytes[:-1]
    elif numBytes[-1] == 'G' or numBytes[-1] == 'g' :
        multiplier = 1<<30
        numBytes = numBytes[:-1]

    try :
        b = float(numBytes)
        if b <= 0 :
            return 512
        else :
            return int(math.ceil(b*multiplier)) # Will always be at least 1.
    except ValueError :
        msg = "%r is not a valid byte size" % numBytes
        raise argparse.ArgumentTypeError(msg)

# Splits up a filename by the dots in the name.
#
def splitFileComponents(filename) :
    fileComponents = filename.split(".")

    # A file with no extension.
    #
    if len(fileComponents) <= 1 :
        return fileComponents

    # Check for extensions with dot (for example, bgeo.sc, bgeo.g, or vdb.gz)
    # and join them before returning result.
    # Note: use of lower() allows us to ignore case of extensions.
    #
    if (".".join(fileComponents[-2:]).lower() in gImageExtList) \
	    or (".".join(fileComponents[-2:]).lower() in gCacheExtList) :

        # If we found a match, join the last two items,
        # into the second last slot, then and delete the last one.
        #
        fileComponents[-2] = ".".join(fileComponents[-2:])
        del fileComponents[-1]

    return fileComponents

# Return two components if "filename" is formatted like a file in a
# sequence otherwise return an empty list.  The two returned
# components are the full filename but missing the frame number,
# and the frame number (with its existing padding if any).
#     Eg.  "a.b.c.001.exr" -> ["a.b.c..exr", "001"]
#          "a.b.c_001.exr" -> ["a.b.c_.exr", "001"]
#
def seqSplit(filename, args) :

    fileComponents = splitFileComponents(filename)

    # A file with no extension.
    #
    if len(fileComponents) <= 1 :
        return []

    # Test if image or cache sequence.
    # Note: use of lower() allows us to ignore case of extensions.
    #
    if (fileComponents[-1].lower() in gImageExtList) \
            or (fileComponents[-1].lower() in gCacheExtList) :

        if not args.strictSeparator :
            looseFileComponents = fileComponents[-2].split("_")
            if len(looseFileComponents) > 1 :
                if isFrameNum(looseFileComponents[-1]) :

                    fileFrameNum = looseFileComponents[-1]
                    looseFileComponents.pop(-1)
                    looseFileComponents[-1] = looseFileComponents[-1] + "_"
                    looseFileKey = "_".join(looseFileComponents)
                    fileComponents[-2] = looseFileKey
                    fileKey = ".".join(fileComponents)
                    return [fileKey, fileFrameNum]

        if len(fileComponents) > 2 and isFrameNum(fileComponents[-2]) :

            fileFrameNum = fileComponents[-2]
            fileComponents.pop(-2)
            fileComponents[-2] = fileComponents[-2] + "."
            fileKey = ".".join(fileComponents)
            return [fileKey, fileFrameNum]

    return []

# Return true if and only if filename is a movie file.
#
def isMovie(filename) :
    fileComponents = filename.split(".")

    # Note: use of lower() allows us to ignore case of extensions.
    #
    return len(fileComponents) > 1 \
        and fileComponents[-1].lower() in gMovieExtList

# Split the filename dictionary KEY into (<imagename>, "", <ext>)
# (empty placeholder for framenum)
#
def splitImageName(filenameKey) :
    numSep = "."
    fileComponents = splitFileComponents(filenameKey)
    if fileComponents[-2] == '' : # because ".." left a blank.
        fileComponents.pop(-2)
    else : # uses "_" separator.
        numSep = '_'
        fileComponents[-2] = fileComponents[-2][:-1] # Strips off the '_'

    fileExt = fileComponents.pop(-1) # (No dot included in string.)
    fileRoot = ".".join(fileComponents) + numSep # Rejoints & tacks back the correct separator.
    return [fileRoot, "", fileExt] # NOTE: fileRoot has the separator attached.

# Return true if and only if keyName (eg. "a.b.c..ass" - from seqSplit())
# is a cache sequence (as opposed to an images sequence).
#
def isCache(keyName) :
    splitName = splitImageName(keyName)
    # use of lower() allows us to ignore case of extensions.
    return splitName[-1].lower() in gCacheExtList

# Reconstruct the imagename with the frame number
# from the dictionary key..
#
def actualImageName(filenameKey, padding, frame) :
    fileParts = splitImageName(filenameKey)
    formatStr = "{0:0=-" + str(padding) + "d}"
    return fileParts[0] + formatStr.format(frame) + "." + fileParts[2]

# Prints an individual sequence based on cmd-line-args.
# frameList comes in sorted from smallest frame number to largest.
#
def printSeq(filenameKey, frameList, args, traversedPath) :

    global gExitStatus

    fileComponents = splitImageName(filenameKey)

    missingFrames = []
    zeroFrames = []
    badFrames = []
    badPadFrames = []
    errFrames = []
    minFrame = frameList[0][FRAME_NUM]
    maxFrame = frameList[-1][FRAME_NUM]
    padding = 0 # Set below, created here for scope.

    # Go through frameList and look for duplicated frame numbers,
    # printing a WARNING when finding duplicates.
    #
    # Throw out duplicates, and arbitrarily keep ONLY the frame with
    # the smallest padding (frameList is already sorted by frame number
    # AND padding). For example: if there is a four-padded sequence,
    #
    #    a.0001.exr, a.0002.exr, a.0003.exr, a.0004.exr
    #
    # But there is also a file,
    #
    #    a.1.exr
    #
    # then due to how padding is calculated below, lsseq will report
    # the sequence as only one-padded, but will report frames 2, 3 and 4
    # as badly-padded. This is probably wrong as far as the user is concerned.
    # But it's up to the user to sort out what's supposed to happen, and how
    # to get rid of the duplicate file, and fix the padding.
    #
    # However a.0001.exr, a.0002.exr, a.0003.exr, a.0004.exr, a.2.exr
    #
    # ...will only report frame 2 as badly padded, also warning about a.0002.exr
    #
    #
    frameListLen = len(frameList)
    uniqueFrameList = [frameList[0]]
    i = 1
    while i < frameListLen :
        if frameList[i][FRAME_NUM] == uniqueFrameList[-1][FRAME_NUM] :
            if not args.silent :
                actualFilename = actualImageName(filenameKey, 
                    uniqueFrameList[-1][FRAME_PADDING], uniqueFrameList[-1][FRAME_NUM])
                duplicateFilename = actualImageName(filenameKey, 
                    frameList[i][FRAME_PADDING], frameList[i][FRAME_NUM])
                sys.stdout.flush()
                sys.stderr.flush()
                print(PROG_NAME, ": warning: ",
                    end='', sep='', file=sys.stderr)
                if args.prependPath != PATH_NOPREFIX and fileComponents[0][0] != '/' :
                    print("sequence: ", traversedPath, sep='', end='', file=sys.stderr)
                    print(fileComponents[0][:-1], ", frame ", frameList[i][FRAME_NUM],
                        ", has duplicate entries: ",
                        os.path.basename(actualFilename), " and ", os.path.basename(duplicateFilename),
                        sep='', file=sys.stderr)
                else :
                    print("sequence ", fileComponents[0][:-1], ", frame ", frameList[i][FRAME_NUM],
                        ", has duplicate entries: ",
                        actualFilename, " and ", duplicateFilename,
                        sep='', file=sys.stderr)
                sys.stderr.flush()
            gExitStatus = gExitStatus | EXIT_LSSEQ_PADDING_WARNING
        else :
            uniqueFrameList.append(frameList[i])
        i += 1

    # Calculate padding.
    #
    # Padding can be calculated from looking at the smallest
    # non-negative integer, or if ALL are negative, then the largest
    # negative integer. Since 1-padding and 2-padding are the same
    # for negative numbers, then it it doesn't matter which one we
    # choose, so we leave it at 2.
    #
    # See example: expandseq --pad 3 -- -11-11
    #         and: expandseq --pad 2 -- -11-11
    # 
    if minFrame >= 0 :
        padding = uniqueFrameList[0][FRAME_PADDING]
    elif maxFrame < 0 :
        padding = uniqueFrameList[-1][FRAME_PADDING]
    else :
        # Find smallest non-negative frame number.
        #
        i = 0
        while uniqueFrameList[i][FRAME_NUM] < 0 :
            i += 1
        padding = uniqueFrameList[i][FRAME_PADDING]

    formatStr = "%0" + str(padding) + "d"

    if args.seqFormat == 'nuke' :
        if minFrame == maxFrame :
            fileComponents[1] = (formatStr % minFrame)
        else :
            fileComponents[1] = "%0" + str(padding) + "d"
        if args.prependPath != PATH_NOPREFIX and fileComponents[0][0] != '/' :
            sys.stdout.write(traversedPath)
        print(fileComponents[0], fileComponents[1], ".", fileComponents[2], sep='', end='')
        if minFrame == maxFrame :
            print()
        else :
            print(" ", str(minFrame), "-", str(maxFrame), sep='')

    elif args.seqFormat == 'shake' :
        if minFrame == maxFrame :
            fileComponents[1] = (formatStr % minFrame)
            print("shake ", sep='', end='')
        else :
            if padding == 4 :
                fileComponents[1] = "#"
            else :
                fileComponents[1] = "@"*padding
            print("shake -t ", str(minFrame), "-", str(maxFrame), " ", sep='', end='')
        if args.prependPath != PATH_NOPREFIX and fileComponents[0][0] != '/' :
            sys.stdout.write(traversedPath)
        else :
            sys.stdout.write("")
        print(fileComponents[0], fileComponents[1], ".", fileComponents[2], sep='')

    elif args.seqFormat == 'glob' :
        if minFrame < 0 :
            fileComponents[1] = "[\-0-9]"
        else :
            fileComponents[1] = "[0-9]"
        if padding > 1 :
            fileComponents[1] = fileComponents[1] + "[0-9]"*(padding-1)

        if args.prependPath != PATH_NOPREFIX and fileComponents[0][0] != '/' :
            sys.stdout.write(traversedPath)
        print(fileComponents[0], fileComponents[1], ".", fileComponents[2], sep='')

    elif args.seqFormat == 'houdini' or args.seqFormat == 'mplay' :
        if minFrame == maxFrame :
            fileComponents[1] = (formatStr % minFrame)
        else :
            fileComponents[1] = "$F"
            if args.seqFormat == 'mplay' :
                fileComponents[1] = "\$F"
            if padding >= 2 :
                fileComponents[1] += str(padding)
        if args.prependPath != PATH_NOPREFIX and fileComponents[0][0] != '/' :
            sys.stdout.write(traversedPath)
        print(fileComponents[0], fileComponents[1], ".", fileComponents[2], sep='')

    elif args.seqFormat == 'rv' :
        if minFrame == maxFrame :
            frameRange = (formatStr % minFrame)
        else :
            padStr = '@' * padding
            if padding == 4 :
                padStr = '#'
            frameRange = str(minFrame) + "-" + str(maxFrame) + padStr
        fileComponents[1] = frameRange

        if args.prependPath != PATH_NOPREFIX and fileComponents[0][0] != '/' :
            sys.stdout.write(traversedPath)
        print(fileComponents[0], fileComponents[1], ".", fileComponents[2], sep='')

    else : # native

        # Gather up the various lists of problem frames.
        # Only needed in native format listings.
        #
        i = minFrame
        while i <= maxFrame :
            iMissing = False
            currFrameData = uniqueFrameList[0]
            if i != currFrameData[FRAME_NUM] :
                iMissing = True
                if args.showMissing :
                    missingFrames.append(i)
            else :
                uniqueFrameList.pop(0)

            if not iMissing :
                if currFrameData[FRAME_MTIME] == FRAME_BROKENLINK :
                    if not args.silent :
                        actualFilename = actualImageName(filenameKey, padding, i)
                        sys.stdout.flush()
                        sys.stderr.flush()
                        print(PROG_NAME, ": warning: ",
                            end='', sep='', file=sys.stderr)
                        if args.prependPath != PATH_NOPREFIX and fileComponents[0][0] != '/' :
                            print(traversedPath, sep='', end='', file=sys.stderr)
                            print(os.path.basename(actualFilename),
                                " is a broken soft link", sep='', file=sys.stderr)
                        else :
                            print(actualFilename, " is a broken soft link", sep='', file=sys.stderr)
                        sys.stderr.flush()
                    gExitStatus = gExitStatus | EXIT_LSSEQ_SOFTLINK_WARNING

            if not iMissing and (args.showZero or args.showBad or args.showBadPadding) :
                if currFrameData[FRAME_MTIME] == FRAME_BROKENLINK :
                    if args.showZero :
                        zeroFrames.append(i)
                    elif args.showBad :
                        badFrames.append(i)

                # File-size issues.
                #
                elif args.showZero and currFrameData[FRAME_SIZE] == 0 :
                    zeroFrames.append(i)
                elif args.showBad and (currFrameData[FRAME_SIZE] < args.goodFrameMinSize) :
                    badFrames.append(i)

                # Bad padding occurs when a number is padded, but shouldn't be,
                # or isn't padded, but it should be.
                #
                if args.showBadPadding and (\
                        (currFrameData[FRAME_PADDING] > len(str(i)) and \
                         currFrameData[FRAME_PADDING] > padding) \
                            or \
                        currFrameData[FRAME_PADDING] < padding) :
                    badPadFrames.append(i)
            i += 1

        if minFrame == maxFrame :
            frameRange = "[" \
                + (formatStr % minFrame) \
                + "]"
        else :
            frameRange = "[" \
                + (formatStr % minFrame) \
                + "-" \
                + (formatStr % maxFrame) \
                + "]"
        fileComponents[1] = frameRange

        if args.prependPath != PATH_NOPREFIX and fileComponents[0][0] != '/' :

            # Strip off any leading "./" from traversedPath. (added v3.0.1)
            #
            if len(traversedPath) > 1 and traversedPath[0:2] == "./" :
                sys.stdout.write(traversedPath[2:])
            else :
                sys.stdout.write(traversedPath)

        if args.extremes :
            fileComponents[1] = formatStr % minFrame
        print(fileComponents[0], fileComponents[1], ".", fileComponents[2], sep='', end='')
        if minFrame != maxFrame and args.extremes :
            print()
            if fileComponents[0][0] != '/' :
                # Strip off any leading "./" from traversedPath. (added v3.0.1)
                #
                if len(traversedPath) > 1 and traversedPath[0:2] == "./" :
                    sys.stdout.write(traversedPath[2:])
                else :
                    sys.stdout.write(traversedPath)
            fileComponents[1] = formatStr % maxFrame
            print(fileComponents[0], fileComponents[1], ".", fileComponents[2], sep='', end='')

        if args.combineErrorFrames :
            errFrames = missingFrames + zeroFrames + badFrames + badPadFrames
            frameSeq = seqLister.condenseSeq(errFrames)
            if len(frameSeq) > 0 :
                sys.stdout.write(" e:[")
                doPrintComma = False
                for f in frameSeq :
                    if doPrintComma :
                        sys.stdout.write(",")
                    sys.stdout.write(f)
                    doPrintComma = True
                sys.stdout.write("]")
            print()
        else :
            missingFrameSeq = seqLister.condenseSeq(missingFrames)
            if len(missingFrameSeq) > 0 :
                sys.stdout.write(" m:[")
                doPrintComma = False
                for f in missingFrameSeq :
                    if doPrintComma :
                        sys.stdout.write(",")
                    sys.stdout.write(f)
                    doPrintComma = True
                sys.stdout.write("]")
            zeroFrameSeq = seqLister.condenseSeq(zeroFrames)
            if len(zeroFrameSeq) > 0 :
                if len(missingFrameSeq) > 0 :
                    sys.stdout.write(",")
                sys.stdout.write(" z:[")
                doPrintComma = False
                for f in zeroFrameSeq :
                    if doPrintComma :
                        sys.stdout.write(",")
                    sys.stdout.write(f)
                    doPrintComma = True
                sys.stdout.write("]")
            badFrameSeq = seqLister.condenseSeq(badFrames)
            if len(badFrameSeq) > 0 :
                if      (len(missingFrameSeq) > 0) or \
                        (len(zeroFrameSeq) > 0) :
                    sys.stdout.write(",")
                sys.stdout.write(" b:[")
                doPrintComma = False
                for f in badFrameSeq :
                    if doPrintComma :
                        sys.stdout.write(",")
                    sys.stdout.write(f)
                    doPrintComma = True
                sys.stdout.write("]")
            badPadFrameSeq = seqLister.condenseSeq(badPadFrames)
            if len(badPadFrameSeq) > 0 :
                if      (len(missingFrameSeq) > 0) or \
                        (len(zeroFrameSeq) > 0) or \
                        (len(badFrameSeq) > 0) :
                    sys.stdout.write(",")
                sys.stdout.write(" p:[")
                doPrintComma = False
                for f in badPadFrameSeq :
                    if doPrintComma :
                        sys.stdout.write(",")
                    sys.stdout.write(f)
                    doPrintComma = True
                sys.stdout.write("]")
            print()

def stripDotFiles(dirContents, stripIt) :
    if not stripIt :
        return dirContents
    else :
        strippedDirContents = []
        for f in dirContents :
            if f[0] != "." :
                strippedDirContents.append(f)
        return strippedDirContents

# This function is recursive and lists the contents passed to it
# via the first argument. Those contents MAY or MAY-NOT be
# all contained in the current working directory. That list will likely
# ONLY be the contents of a single directory if this has been
# called recursively with "-R" to lsseq, and we're more than one level deep.
#
# This fucntion assumes that if a directory-title is needed
# (i.e., the dirContents parameter to this function), for example:
#
# dirName:
# aaa bbb ccc etc
#
# ...then that title "dirName:" is printed BEFORE the call to this function.
#
# The function arguments are as follows:
# 
#   dirContents - This might be a list from the command line,
#                 OR generated from a recursive descent into a directory.
#          path - The directory we need to descend into, and pop out of.
#                 (Might be trivially "." if called from main())
#   listSubDirs - Boolean. ONLY ever True if called from main() .
#                 This arg allows us to get ONE LEVEL of recursion only.
#                 unless args.isRecursive is also True in which
#                 case we may descend further if need be.
#          args - The all the args set on the command line.
# traversedPath - The path descended so far to get to this level
#                 used to print the directory-title. Also note that
#                 traversedPath will always have a '/' as the last
#                 character in the string.
# 
def listSeqDir(dirContents, path, listSubDirs, args, traversedPath) :

    # Declare global variables since they might be modified by this function.
    #
    global gTimeList
    global gImageDictionary
    global gCacheDictionary
    global gMoviesDictionary
    global gExitStatus

    # Stash the current working dir, to come back to and the end
    # of this function. I.e.; we need to push and pop the current
    # working directory ourselves since it has global scope in
    # python.
    #
    tmpCWD = os.path.abspath(".")
    os.chdir(path) # Note: path might be "." if coming from main() 

    # Following flag set iff something got printed here before reaching
    # printing of subdirs.
    #
    somethingWasPrinted = False

    # The 'imageDictionary' (and 'cacheDictionary') has <imageName>..<ext>
    # (or <imageName>_.<ext>), i.e., name without the frame number, as the
    # key for each entry.  Each entry is a list containing four-tuples,
    # namely:
    #
    #     [ (frameNum, fileSize, mtime, padding), ... ]
    #
    # The 'moviesDictionary' has the movie file name as the key, and the
    # file size as the data stored.  It stores -1 for the file size if the
    # file is invalid.
    #
    imageDictionary = {}
    cacheDictionary = {}
    moviesDictionary = {}
    otherFiles = []
    dirList = []

    # Go through the directory contents sifting out the various file types,
    # collect the names into various lists for printing after this is done.
    #
    for filename in dirContents :

        # If the file is a directory, regardless of what it is called,
        # then CLEARLY it is NOT part of an image sequence.
        #
        if os.path.isdir(filename) :
            if (not listSubDirs or not args.listDirContents) \
                    and args.listWhichFiles == LIST_ALLFILES :
                otherFiles.append(filename)
            dirList.append(filename)

        else :

            fileParts = seqSplit(filename, args)
            if len(fileParts) == 2 : # Means file is an image or cache.
                newFrameNum = int(fileParts[FRAMENUM])
                newPaddingSize = len(fileParts[FRAMENUM])

                # Check to see if file exists - might be broken soft link.
                if not os.path.exists(filename) :
                    newFrameSize = 0
                    newFrameMTime = FRAME_BROKENLINK
                else :
                    realFilename = os.path.realpath(filename)
                    newFrameSize = os.path.getsize(realFilename)
                    newFrameMTime = os.path.getmtime(realFilename)

                if isCache(fileParts[SEQKEY]) :
                    if fileParts[SEQKEY] in cacheDictionary :
                        # tack on new frame number.
                        cacheDictionary[fileParts[SEQKEY]].append(
                            (newFrameNum, newFrameSize, newFrameMTime, newPaddingSize))
                    else :
                        # initialiaze dictionary entry.
                        cacheDictionary[fileParts[SEQKEY]] = [
                            (newFrameNum, newFrameSize, newFrameMTime, newPaddingSize)]
                else :
                    if fileParts[SEQKEY] in imageDictionary :
                        # tack on new frame number.
                        imageDictionary[fileParts[SEQKEY]].append(
                            (newFrameNum, newFrameSize, newFrameMTime, newPaddingSize))
                    else :
                        # initialiaze dictionary entry.
                        imageDictionary[fileParts[SEQKEY]] = [
                            (newFrameNum, newFrameSize, newFrameMTime, newPaddingSize)]

            elif isMovie(filename) :
                # Check to see if file exists - might be broken soft link.
                if not os.path.exists(filename) :
                    moviesDictionary[filename] = FRAME_BROKENLINK
                else :
                    realFilename = os.path.realpath(filename)
                    moviesDictionary[filename] = os.path.getmtime(realFilename)

            # filename is neither part of an image sequence, NOR a movie file
            # Add it to otherfiles if we need to list those as well.
            #
            elif args.listWhichFiles == LIST_ALLFILES :
                    otherFiles.append(filename)

    # Use actual "ls" to print non-image files nicely.
    #
    otherFiles.sort()
    if len(otherFiles) > 0 :
        extra_ls_options = []
        if args.classify :
            extra_ls_options.append("-F")

        if args.byWhat == BY_SINGLE : # byWhat values are mutually exclusive.
            extra_ls_options.append("-1")
        elif args.byWhat == BY_COLUMNS :
            extra_ls_options.append("-C")
        elif args.byWhat == BY_ROWS :
            extra_ls_options.append("-x")

        if args.sortByMTime :
            extra_ls_options.append("-t")

        if args.reverseListing :
            extra_ls_options.append("-r")

        # Note: v2.7.* and earlier version of lsseq used subprocess.call('ls')
        # Which did not intercept stdout, so it calculated columns 
        # properly based on if stdout was a terminal or not.
        #
        # Now, as of v3.0.0, we are using subprocess.run('ls', capture_output=True"),
        # so 'ls' doesn't understand if lsseq's stdout is connected to stdout or not.
        # Now we need to duplicate ls's internal logic ourselves to set the output
        # correctly. We will set an env-var "COLUMNS" as used by 'ls' to acheive this.
        
        # "COLUMNS" is a variable that is used by 'ls' on BOTH Linux AND Darwin,
        # for setting the width for both '-C' and '-x', but its use is only
        # documented on Darwin (see man ls(1)).
        #
        # However COLUMNS is NOT an enviroment-variable by default. Which isn't
        # to say that someone might not have 'exported' it as such on purpose.
        #
        # As you can see from the following cmds that were run in a
        # 'terminal' on RHEL 8 (actually AlmaLinux release 8.8):
        #
        #    $ echo $COLUMNS
        #    110
        #    $ cat printColumns 
        #    #!/bin/bash
        #    echo COLUMNS $COLUMNS
        #    $ ./printColumns 
        #    COLUMNS
        #    $ export COLUMNS
        #    $ ./printColumns 
        #    COLUMNS 110
        #    $ export -n COLUMNS
        #    $ ./printColumns 
        #    COLUMNS
        #    $ source printColumns 
        #    COLUMNS 110
        #
        # ...and from further experimentation, '/bin/ls' respects 'COLUMNS' and
        # its treatment of stdout as a tty or pipe or redirect, also as relates
        # to -C and -x etc. 

        # shutil.get_terminal_size() returns the value of COLUMNS (if set as
        # env-var by the caller AND when it's a valid positive integer) and also
        # returns a decent default if not an env-var AND stdout is not a tty.
        # 
        # Then we set COLUMNS as an env-var so our call to 'ls' picks it up properly.
        #
        cols, rows = shutil.get_terminal_size()
        os.environ["COLUMNS"] = str(cols)

        # No '-1', '-C' or '-x' used on cmd-line.
        # So, if stdout is a tty, then behave as if '-C' was set,
        # which is standard 'ls' behavior.
        #
        if args.byWhat == BY_UNSPECIFIED and sys.stdout.isatty():
            extra_ls_options.append("-C")

        extra_ls_options.append("--")
        lsCmd = ["ls", "-d"] + extra_ls_options + otherFiles

        sys.stdout.flush()
        sys.stderr.flush()
        lsResult = subprocess.run(lsCmd, capture_output=True, text=True)

        if lsResult.returncode > 0 :
            if not args.silent :
                print(PROG_NAME, " : ", lsResult.stderr,
                    file=sys.stderr, sep='', end='') # ls error message contains newline
                sys.stderr.flush()

            # Don't actually exit - but like 'ls', finish doing the work
            # but exit with non-zero exit-status at the end of the program.
            #
            gExitStatus = gExitStatus | EXIT_LS_ERROR

        if len(lsResult.stdout) > 0 :
            print(lsResult.stdout, end='') # ls output contains newlines
            sys.stdout.flush()
            somethingWasPrinted = True

    # Now actually print the sequences in this directory.
    #
    if args.listWhichFiles == LIST_ONLYIMGS :
        seqKeys = list(imageDictionary.keys())
    elif args.listWhichFiles == LIST_ONLYMOVS :
        seqKeys = list(moviesDictionary.keys())
    elif args.listWhichFiles == LIST_ONLYCACHES :
        seqKeys = list(cacheDictionary.keys())
    else :
        seqKeys = list(imageDictionary.keys())
        movKeys = list(moviesDictionary.keys())
        cacheKeys = list(cacheDictionary.keys())
        for k in movKeys :
            seqKeys.append(k)
        for k in cacheKeys :
            seqKeys.append(k)

    # Gather file mod times if needed.
    #
    timeList = []
    if args.sortByMTime or args.cutoffTime != None : # non-null cutoffTime means need time compare
        for k in seqKeys :

            if isMovie(k) :
                # Note: only thing stored in "moviesDictionary" is the mod-time of the file.
                timeList.append((k, int(moviesDictionary[k])))

            elif isCache(k) :
                validTimes = []
                for im in cacheDictionary[k] :
                    if im[FRAME_MTIME] != FRAME_BROKENLINK :
                        validTimes.append(im[FRAME_MTIME])
                validTimes.sort()
                time = 0
                n = len(validTimes)
                if n == 1 :
                    time = validTimes[0]
                elif n > 1 :
                    if args.timeCompare == 'oldest' :
                        time = validTimes[0]
                    elif args.timeCompare == 'median' :
                        midIndex = int(math.floor(n/2))
                        if n % 2 == 1 : # Odd number of items
                            time = validTimes[midIndex]
                        else : # Even number of items.
                            time = (validTimes[midIndex] + validTimes[midIndex-1])/2
                    else : # newest
                        time = validTimes[-1]
                timeList.append((k, int(time)))

            else : # key is an image.
                validTimes = []
                for im in imageDictionary[k] :
                    if im[FRAME_MTIME] != FRAME_BROKENLINK :
                        validTimes.append(im[FRAME_MTIME])
                validTimes.sort()
                time = 0
                n = len(validTimes)
                if n == 1 :
                    time = validTimes[0]
                elif n > 1 :
                    if args.timeCompare == 'oldest' :
                        time = validTimes[0]
                    elif args.timeCompare == 'median' :
                        midIndex = int(math.floor(n/2))
                        if n % 2 == 1 : # Odd number of items
                            time = validTimes[midIndex]
                        else : # Even number of items.
                            time = (validTimes[midIndex] + validTimes[midIndex-1])/2
                    else : # newest
                        time = validTimes[-1]
                timeList.append((k, int(time)))

    if args.sortByMTime :
        if args.globalSortByTime :
            #
            # Append sequences to the global list for later printing.
            # then print nothing and continue below (recursive descent,
            # or processing other directory contents). Need to extend
            # the tuple in gTimeList to include "traversedPath" since
            # that string won't be availabe when we finally emerge from
            # listSeqDir() in main(). Also need copies of the dictionaries 
            # saved globally for use in main(), but the key needs to 
            # be extended to include traversedPath to get unique keys
            # globally.
            #
            for seq in timeList :
                gTimeList.append( (seq[DICTKEY], seq[MTIME], traversedPath) )
                gDictKey = traversedPath + '/' + seq[DICTKEY]
                if isMovie(seq[DICTKEY]) :
                    gMoviesDictionary[gDictKey] = moviesDictionary[seq[DICTKEY]]
                elif isCache(seq[DICTKEY]) :
                    gCacheDictionary[gDictKey] = cacheDictionary[seq[DICTKEY]]
                else :
                    gImageDictionary[gDictKey] = imageDictionary[seq[DICTKEY]]
        else :
            timeList.sort(key=itemgetter(MTIME)) # Sorts by time.
            # Note: ls -t prints newest first; ls -tr is newest last.
            if not args.reverseListing :
                timeList.reverse()
            for seq in timeList :
                if args.cutoffTime != None :
                    if args.cutoffTime[0] == 'before' :
                        if seq[MTIME] > args.cutoffTime[1] :
                            continue
                    else : # Guaranteed to be 'since'
                        if seq[MTIME] < args.cutoffTime[1] :
                            continue
                if isMovie(seq[DICTKEY]) :
                    if args.prependPath != PATH_NOPREFIX :
                        sys.stdout.write(traversedPath)
                    print(seq[DICTKEY])
                    somethingWasPrinted = True
                elif isCache(seq[DICTKEY]) :
                    cacheDictionary[seq[DICTKEY]].sort(key=itemgetter(FRAME_NUM, FRAME_PADDING))
                    printSeq(seq[DICTKEY], cacheDictionary[seq[DICTKEY]], args, traversedPath)
                    somethingWasPrinted = True
                else :
                    imageDictionary[seq[DICTKEY]].sort(key=itemgetter(FRAME_NUM, FRAME_PADDING))
                    printSeq(seq[DICTKEY], imageDictionary[seq[DICTKEY]], args, traversedPath)
                    somethingWasPrinted = True
    elif args.cutoffTime != None :
        timeList.sort(key=itemgetter(DICTKEY)) # Sorts by name.
        if args.reverseListing :
            timeList.reverse()
        for seq in timeList :
            if args.cutoffTime[0] == 'before' :
                if seq[MTIME] > args.cutoffTime[1] :
                    continue
            else : # Guaranteed to be 'since'
                if seq[MTIME] < args.cutoffTime[1] :
                    continue
            if isMovie(seq[DICTKEY]) :
                if args.prependPath != PATH_NOPREFIX :
                    sys.stdout.write(traversedPath)
                print(seq[DICTKEY])
                somethingWasPrinted = True
            elif isCache(seq[DICTKEY]) :
                cacheDictionary[seq[DICTKEY]].sort(key=itemgetter(FRAME_NUM, FRAME_PADDING))
                printSeq(seq[DICTKEY], cacheDictionary[seq[DICTKEY]], args, traversedPath)
                somethingWasPrinted = True
            else :
                imageDictionary[seq[DICTKEY]].sort(key=itemgetter(FRAME_NUM, FRAME_PADDING))
                printSeq(seq[DICTKEY], imageDictionary[seq[DICTKEY]], args, traversedPath)
                somethingWasPrinted = True
    else :
        seqKeys.sort()
        if args.reverseListing :
            seqKeys.reverse()
        for k in seqKeys :
            if isMovie(k) :
                if args.prependPath != PATH_NOPREFIX :
                    sys.stdout.write(traversedPath)
                print(k)
                somethingWasPrinted = True
            elif isCache(k) :
                cacheDictionary[k].sort(key=itemgetter(FRAME_NUM, FRAME_PADDING))
                printSeq(k, cacheDictionary[k], args, traversedPath)
                somethingWasPrinted = True
            else :
                imageDictionary[k].sort(key=itemgetter(FRAME_NUM, FRAME_PADDING))
                printSeq(k, imageDictionary[k], args, traversedPath)
                somethingWasPrinted = True

    # lsseq the contents of any subdirectories if need be.
    #         Somewhat mimics the calls up in main().
    #
    firstDir = True
    if (listSubDirs or args.isRecursive) and args.listDirContents :
        dirList.sort()
        for d in dirList :
            if d[-1] == "/" :
                d = d[:-1]
            if args.prependPath == PATH_NOPREFIX :
                if somethingWasPrinted or not firstDir :
                    print()
                firstDir = False
                if args.isRecursive :
                    print(traversedPath, d, ":", sep='')
                else :
                    print(d, ":", sep='')

            if d[0] == "/" :
                passedPath = d + "/"
            else :
                passedPath = traversedPath + d + "/"

            listSeqDir(stripDotFiles(os.listdir(d), args.ignoreDotFiles),
                d, False, args, passedPath)

    os.chdir(tmpCWD) # Pop the stack of directories.

def main() :

    # Redefine the exception handling routine so that it does NOT
    # do a trace dump if the user types ^C while lsseq is running.
    #
    old_excepthook = sys.excepthook
    def new_hook(exceptionType, value, traceback) :
        if exceptionType != KeyboardInterrupt and exceptionType != IOError :
            old_excepthook(exceptionType, value, traceback)
        else :
            pass
    sys.excepthook = new_hook

    # These global variables might be changed below depending on
    # whether some environment variables are set.
    #
    global gImageExtList
    global gMovieExtList
    global gCacheExtList
    global gExitStatus

    # To help with argparse.
    #
    # This block of code allows us to set multiple values at once with
    # one flag. I will use it to clear a bunch of toggles with one option
    # on the command line. The beauty of this is that we can use this flag
    # to clear all of the toggles, but then reset ONLY ONE later on the
    # command line as argparse sets the values as it marches through the options.
    #
    def store_const_multiple(const, *destinations) :
        class store_const_multiple_action(argparse.Action) :
            def __init__(self, *args, **kwargs) :
                super(store_const_multiple_action, self).__init__(
                    metavar = None, nargs = 0, const = const, *args, **kwargs)
            def __call__(self, parser, namespace, values, option_string = None) :
                for d in destinations :
                    setattr(namespace, d, const)
        return store_const_multiple_action

    def store_false_multiple(*destinations) :
        return store_const_multiple(False, *destinations)

    p = argparse.ArgumentParser(
        prog=PROG_NAME,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
            List directory contents like /bin/ls except condense image
            sequences to one entry each. Filenames that are part of image
            sequences are assumed to be of the form:

                <descriptiveName>.<frameNum>.<imgExtension>

            where <imgExtension> is drawn from a default list of image extensions
            (displayed with option --imgExt) or alternatively from the environment
            variable LSSEQ_IMAGE_EXTENSION which should contain a colon separated
            list of image file extensions.

            %(prog)s first lists all non-image-sequence files followed by the
            list of image sequences as such:

                $ %(prog)s
                [output of /bin/ls minus image sequences]
                [list of images sequences]
            '''),
        usage="%(prog)s [-h | --help] [OPTION]... [FILE]...")

    p.add_argument("--version", action="version", version=VERSION)

    p.add_argument("--format", "-f", action="store", type=str,
        choices=("native", "nuke", "rv", "shake", "glob", "mplay", "houdini"),
        dest="seqFormat",
        metavar="FORMAT",
        default="native",
        help="list image sequences in various formats.\
        The choices are 'native' (default), 'nuke', 'rv', 'shake', 'glob', \
        'mplay', and 'houdini'.\
        Note that glob prints correct results only if \
        the frame numbers are padded. Further note that reporting of \
        missing/bad/etc frames (e.g. --showMissing) only happens \
        with 'native' format")
    p.add_argument("--showMissing", "-m", action="store_true",
        dest="showMissing", default=True,
        help="show list of missing frames as 'm:[<list>]' [default]" )
    p.add_argument("--skipMissing", "-M", action="store_false",
        dest="showMissing",
        help="do not show list of missing frames" )
    p.add_argument("--showZero", "-z", action="store_true",
        dest="showZero", default=True,
        help="show list of zero length images as 'z:[<list>]' [default]" )
    p.add_argument("--skipZero", "-Z", action="store_false",
        dest="showZero",
        help="do not show list of zero length images" )
    p.add_argument("--showBadFrames", "-b", action="store_true",
        dest="showBad", default=False,
        help="lists potentially bad frames based on the \
        minimum size of a good frame (see --goodFrameMinSize). \
        Reported as 'b:[<list>]'")
    p.add_argument("--skipBadFrames", "-B", action="store_false",
        dest="showBad",
        help="do not show list of potentially bad frames [default]" )
    p.add_argument("--goodFrameMinSize", action="store", type=readByteShortForm,
        dest="goodFrameMinSize", default=512,
        metavar="BYTES",
        help="any frame size less than BYTES is \
        a bad frame. Short forms for byte sizes are accepted as \
        in '1K' (i.e., 1024) or '1.5K' for example. [default: 512]")
    p.add_argument("--showBadPadding", "-g", action="store_true",
        dest="showBadPadding", default=True,
        help="report badly padded frame numbers which occurs when a number is padded \
        but shouldn't be, or isn't padded but it should be. Reported as 'p:[<list>]' [default]")
    p.add_argument("--skipBadPadding", "-G", action="store_false",
        dest="showBadPadding",
        help="do not show list of badly padded frames" )
    p.add_argument("--combineLists", "-c", action="store_true",
        dest="combineErrorFrames", default=False,
        help="combine the lists of zero, missing and bad frames into one list. \
        Reported as 'e:[<list>]'")
    p.add_argument("--noCombineLists", action="store_false",
        dest="combineErrorFrames",
        help="Don't combine the error lists")
    p.add_argument("--noErrorLists", "-n", help = "Skip printing ALL error lists. \
        Note: Setting --showBadPadding (for example) AFTER this \
        option on the command line has the effect of ONLY \
        showing the badPadding error list ", \
        action = store_false_multiple("showMissing", "showZero", "showBad", "showBadPadding"))
    p.add_argument("--looseNumSeparator", "-l", action="store_false",
        dest="strictSeparator",
        help="allow the use of '_' (underscore), in addition to '.' (dot) \
            as a separator between the descriptiveName and frameNumber when \
            looking to interpret filenames as \
            image sequences. i.e., <descriptiveName>_<frameNum>.<imgExtension> \
            (also see --strictNumSeparator)")
    p.add_argument("--strictNumSeparator", "-s", action="store_true",
        dest="strictSeparator", default=True,
        help="strictly enforce the use of '.' (dot) as a separator between the \
            descriptiveName and frameNumber when looking to interpret filenames as \
            image sequences. i.e., <descriptiveName>.<frameNum>.<imgExtension> \
            (also see --looseNumSeparator) [default]")

    p.add_argument("--onlySequences", "-o", action="store_const",
        dest="listWhichFiles", default=LIST_ALLFILES, const=LIST_ONLYSEQS,
        help="only list image sequences, cache sequences and movies")
    p.add_argument("--onlyImages", "-O", action="store_const",
        dest="listWhichFiles", const=LIST_ONLYIMGS,
        help="strictly list only image sequences (i.e., no movies or caches)")
    p.add_argument("--onlyMovies", action="store_const",
        dest="listWhichFiles", const=LIST_ONLYMOVS,
        help="strictly list only movies (i.e., no images or caches)")
    p.add_argument("--onlyCaches", action="store_const",
        dest="listWhichFiles", const=LIST_ONLYCACHES,
        help="strictly list only cache sequences (i.e., no images or movies)")
    p.add_argument("--imgExt", "-i", action="store_true",
        dest="printImgExtensions", default=False,
        help="print list of image, cache and movie file extensions and exit")

    p.add_argument("--prependPathAbs", "-p", action="store_const",
        dest="prependPath", default=PATH_NOPREFIX, const=PATH_ABS,
        help="prepend the absolute path name to the image name. \
        This option implies the option --onlySequences and also \
        suppresses printing directory name headers when listing \
        directory contents")
    p.add_argument("--prependPathRel", "-P", action="store_const",
        dest="prependPath", const=PATH_REL,
        help="prepend the relative path name to the image name. \
        This option implies the option --onlySequences and will also \
        suppress printing directory name headers when listing \
        directory contents")
    p.add_argument("--extremes", "-e", action="store_true",
        dest="extremes", default=False,
        help="only list the first and last image on a separate line each. \
        This option implies --prependPathAbs (unless --prependPathRel is \
        explicitly specified) and --onlySequences")

    p.add_argument("--single", "-1", action="store_const",
        dest="byWhat", default=BY_UNSPECIFIED, const=BY_SINGLE,
        help="list one non-sequence entry per line (see ls(1))")
    p.add_argument("--all", "-a", action="store_false",
        dest="ignoreDotFiles", default=True,
        help="do not ignore entries starting with '.' \
        while omitting implied '.' and '..' directories (see ls(1) --almost-all)")
    p.add_argument("--byColumns", "-C", action="store_const",
        dest="byWhat", const=BY_COLUMNS,
        help="list non-sequence entries by columns (see ls(1))")
    p.add_argument("--byRows", "-x", action="store_const",
        dest="byWhat", const=BY_ROWS,
        help="list non-sequence entries by lines instead of by columns (see ls(1))")
    p.add_argument("--directory", "-d", action="store_false",
        dest="listDirContents", default=True,
        help="list directory entries instead of contents, \
        and do not dereference symbolic links (see ls(1))")
    p.add_argument("--classify", "-F", action="store_true",
        dest="classify", default=False,
        help="append indicator (one of */=>@|) to entries (see ls(1))")
    p.add_argument("--reverse", "-r", action="store_true",
        dest="reverseListing", default=False,
        help="reverse order while sorting")
    p.add_argument("--recursive", "-R", action="store_true",
        dest="isRecursive", default=False,
        help="list subdirectories recursively")
    p.add_argument("-t", "--sortByTime", action="store_true",
        dest="sortByMTime", default=False,
        help="sort by modification time, the default comparison \
        time is between the most recently modified (newest) frames \
        in each sequence. (see --time) (see ls(1))")
    p.add_argument("--time", action="store", type=str,
        dest="timeCompare",
        help="which frame in the sequence to use to compare times \
        between sequences when sorting by time. The possible values \
        for 'FRAME_AGE' are 'oldest', 'median' and 'newest' \
        [default: 'newest']", metavar="FRAME_AGE", default="newest",
        choices=("oldest", "median", "newest"))
    p.add_argument("--onlyShow", action="store", type=str, nargs=2,
        dest="cutoffTime",
        help="where TENSE is either 'before' or 'since'; only list sequences \
        up to (and including) or after (and including) the time specified. The --time argument \
        specifies which frame to use for the cutoff comparison. \
        The optional CC (century) defaults to the current century. \
        The optional '-hh' (hours), 'mm' (minutes) or 'ss' (seconds) \
        default to zero if not specified.",
        metavar=("TENSE", "[CC]YYMMDD[-hh[mm[ss]]]"))
    p.add_argument("--globalSortByTime", action="store_true",
        dest="globalSortByTime", default=False,
        help="when using either \
        --prependPathAbs or --prependPathRel then this option will sort ALL \
        sequences by time compared to each other, as opposed to only sorting \
        sequences by time within their common directory. If the above conditions \
        are NOT met, then this option is simply ignored.")
    p.add_argument("--silent", "--quiet", action="store_true",
        dest="silent", default=False,
        help="suppress error and warning messages")

    p.add_argument("files", metavar="FILE", nargs="*",
        help="file names")

    args = p.parse_args()

    # Grab environment variables if they exist and clean them
    # up if they contain gargage..
    #
    tmpExt = os.getenv("LSSEQ_IMAGE_EXTENSION")
    tmpOICExt = os.getenv("OIC_IMAGE_EXTENSION")
    if tmpExt != None and tmpExt != "" :
        tmpExtList = tmpExt.split(":")
    elif tmpOICExt != None and tmpOICExt != "" :
        tmpExtList = tmpOICExt.split(":")
    else :
        tmpExtList = gImageExtList
    #
    # Using a set below removes duplicates if they exist.
    #
    # Also: Use of lower() allows us to ignore case of file extensions.
    # We store our list entries below as lowercase, then compare file
    # extenstions (that have been converted to lowercase) against
    # these lists.
    #
    tmpExtSet = set([])
    for e in tmpExtList :
        tmpExtSet.add(e.lower())
    tmpExtList = sorted(tmpExtSet)
    gImageExtList = copy.deepcopy(tmpExtList)

    tmpExt = os.getenv("LSSEQ_MOV_EXTENSION")
    tmpOICExt = os.getenv("OIC_MOV_EXTENSION")
    if tmpExt != None and tmpExt != "" :
        tmpExtList = tmpExt.split(":")
    elif tmpOICExt != None and tmpOICExt != "" :
        tmpExtList = tmpOICExt.split(":")
    else :
        tmpExtList = gMovieExtList
    # Using a set like this removes duplicates if they exist.
    tmpExtSet = set([])
    for e in tmpExtList :
        tmpExtSet.add(e.lower())
    tmpExtList = sorted(tmpExtSet)
    gMovieExtList = copy.deepcopy(tmpExtList)

    tmpExt = os.getenv("LSSEQ_CACHE_EXTENSION")
    tmpOICExt = os.getenv("OIC_CACHE_EXTENSION")
    if tmpExt != None and tmpExt != "" :
        tmpExtList = tmpExt.split(":")
    elif tmpOICExt != None and tmpOICExt != "" :
        tmpExtList = tmpOICExt.split(":")
    else :
        tmpExtList = gCacheExtList
    # Using a set like this removes duplicates if they exist.
    tmpExtSet = set([])
    for e in tmpExtList :
        tmpExtSet.add(e.lower())
    tmpExtList = sorted(tmpExtSet)
    gCacheExtList = copy.deepcopy(tmpExtList)

    #
    # Respond to arguments set by user and/or set up variables
    # etc. needed later based on the user's arguments.
    #

    if args.printImgExtensions :
        print(PROG_NAME, ": Modify the following environment variables to extend the supported file types.", sep='')
        print("       NOTE: ", PROG_NAME, " also recognizes the following extensions when uppercase.", sep='')
        extList = ":".join(gImageExtList)
        print("  export LSSEQ_IMAGE_EXTENSION=", extList, sep='')
        extList = ":".join(gMovieExtList)
        print("  export LSSEQ_MOV_EXTENSION=", extList, sep='')
        extList = ":".join(gCacheExtList)
        print("  export LSSEQ_CACHE_EXTENSION=", extList, sep='')
        sys.exit(EXIT_NO_ERROR)

    if args.prependPath == PATH_REL :
        if args.listWhichFiles == LIST_ALLFILES :
            args.listWhichFiles = LIST_ONLYSEQS

    if args.prependPath == PATH_ABS :
        if args.listWhichFiles == LIST_ALLFILES :
            args.listWhichFiles = LIST_ONLYSEQS

    if args.extremes :
        if args.prependPath == PATH_NOPREFIX :
            args.prependPath = PATH_ABS
        args.showMissing = False
        args.showZero = False
        args.showBad = False
        args.showBadPadding = False
        args.seqFormat = 'native'
        if args.listWhichFiles == LIST_ALLFILES :
            args.listWhichFiles = LIST_ONLYIMGS # Strictly only images.

    if args.cutoffTime != None :

        # Do they want sequences 'before' or 'since' a given date?
        #
        args.cutoffTime[0] = args.cutoffTime[0].lower()
        if (args.cutoffTime[0] != 'before') and (args.cutoffTime[0] != 'since') :
            if not args.silent :
                print(PROG_NAME,
                    ": error: argument --onlyShow: TENSE must be 'since' or 'before'",
                    file=sys.stderr, sep='')
            sys.exit(gExitStatus | EXIT_ARGPARSE_ERROR) # Doing our own 'argparse' checks here.

        from datetime import datetime

        # Process the cutoff time set.
        # Loop through list of acceptable formats declared globally.
        #
        matchedDate = False
        for dateFormat in DATE_FORMAT_LIST :
            try:
                timeData = datetime.strptime(args.cutoffTime[1], dateFormat[0])

                # Make sure the prior strptime() call matched against a string
                # with zero padding for month, day, etc. If the length of the matched
                # string doesn't add up to what it should be if zero padded
                # then reject the match and keep looping.
                #
                # This test is needed since strptime() does not ENFORCE zero
                # padding of months, days, minutes etc. leading to possible
                # ambiguity and thus is an undesireable feature of strptime().
                #
                # This code works around that limitation.
                #
                if len(args.cutoffTime[1]) == dateFormat[1] :
                    matchedDate = True
                    break

            except ValueError as ve:
                # Note, we could probably make clever use of the ValueError
                # reported here, but since we have a list of possible formats
                # sorting it out if everthing fails seems like more trouble
                # than it's worth.
                #
                continue

        if not matchedDate :
            if not args.silent :
                print(PROG_NAME,
                    ": error: argument --onlyShow: the time must be of the form [CC]YYMMDD[-hh[mm[ss]]]",
                    file=sys.stderr, sep='')
            sys.exit(gExitStatus | EXIT_ARGPARSE_ERROR)

        import time
        args.cutoffTime[1] = int(time.mktime(timeData.timetuple())) # Epoch time

    # args.globalSortByTime is only used in the code above to defer printing
    # the sequences until the end, after ALL the sequences been collected into
    # a common dictionary. We check the validity of the other command-line
    # options to determine if this flag should be set (see help description above).
    # Also we need to turn on args.sortByMTime so that some code above gets
    # excuted which captures times etc.
    #
    if args.globalSortByTime :
        if args.prependPath == PATH_NOPREFIX :
            args.globalSortByTime = False
        else :
            args.sortByMTime = True # Needed to engage code to capture times

    # Now the meat and potatoes.
    # The following logic attempts to mimic the behavior
    # of /bin/ls as closely as possible.

    # No args means list the current directory.
    #
    if len(args.files) == 0 :
        if not args.listDirContents :
            if args.listWhichFiles == LIST_ALLFILES :
                print(".") # Yup, we're done!
        else :
            if args.isRecursive :
                if args.prependPath == PATH_NOPREFIX :
                    print(".:")
                passedPath = "./"
            else :
                passedPath = ""
            if args.prependPath == PATH_ABS :
                passedPath = os.getcwd() + "/"

            listSeqDir(stripDotFiles(os.listdir("."), args.ignoreDotFiles), ".", False, args, passedPath)

    # We are being asked to list a specific directory, so we don't need
    # to print the directory name before listing the contents (unless
    # it is a recursive listing).  (/bin/ls behavior.)
    #
    elif len(args.files) == 1 and os.path.isdir(args.files[0]) and args.prependPath != PATH_ABS :
        arg0 = args.files[0]
        # Strip out trailing "/" that may have been tacked on by
        # file completion.  (/bin/ls does not do this - but it's
        # cleaner looking.)
        #
        if args.files[0][-1] == "/" :
            arg0 = args.files[0][:-1]

        if not args.listDirContents :
            print(arg0) # Yes, we're done here too.

        else :

            if args.isRecursive : # The case where we do need to print the dir "title".
                if args.prependPath == PATH_NOPREFIX :
                    print(arg0, ":", sep='')
                passedPath = arg0 + "/"
            else :
                passedPath = ""

            if args.prependPath == PATH_REL :
                passedPath = arg0 + "/"

            if args.prependPath == PATH_ABS :
                passedPath = os.getcwd() + "/"

            # Here's a case where we're being asked to list a directory that we might
            # not even be in, i.e., it's an absolute path to another directory than
            # the current working directory.
            #
            if arg0[0] == "/" :
                passedPath = arg0 + "/"

            listSeqDir(stripDotFiles(os.listdir(arg0), args.ignoreDotFiles), arg0, False, args, passedPath)

    # List all the arguments on the command line and unless prevented by
    # the "-d" option, it will also list the contents of all the directories
    # entered on the command line. (Facilitated by the 3rd arg 'True' below.)
    # This 3rd boolean argument is a way of getting only one level of descent.
    # This is the ONLY place that True is passed listSeqDir().
    #
    else :
        passedPath = ""
        if args.prependPath == PATH_ABS :
            passedPath = os.getcwd() + "/"
        listSeqDir(args.files, ".", True, args, passedPath)


    # If we need to print the sequences globally sorted by time,
    # we do it here, note that in this case nothing will have been
    # printed so far. Also we know that args.prependPath != PATH_NOPREFIX
    # since this option is turned OFF if this is not the case.
    #
    if args.globalSortByTime :
        gTimeList.sort(key=itemgetter(MTIME)) # Sorts by time.
        # Note: ls -t prints newest first; ls -tr is newest last.
        if not args.reverseListing :
            gTimeList.reverse()
        for seq in gTimeList :
            if args.cutoffTime != None :
                if args.cutoffTime[0] == 'before' :
                    if seq[MTIME] > args.cutoffTime[1] :
                        continue
                else : # Guaranteed to be 'since'
                    if seq[MTIME] < args.cutoffTime[1] :
                        continue
            gDictKey = seq[TRAVERSEDPATH] + '/' + seq[DICTKEY]
            if isMovie(seq[DICTKEY]) :
                print(gDictKey)
            elif isCache(seq[DICTKEY]) :
                gCacheDictionary[gDictKey].sort(key=itemgetter(FRAME_NUM, FRAME_PADDING))
                printSeq(seq[DICTKEY], gCacheDictionary[gDictKey], args, seq[TRAVERSEDPATH])
            else :
                gImageDictionary[gDictKey].sort(key=itemgetter(FRAME_NUM, FRAME_PADDING))
                printSeq(seq[DICTKEY], gImageDictionary[gDictKey], args, seq[TRAVERSEDPATH])

    sys.exit(gExitStatus)

if __name__ == '__main__' :
    main()
