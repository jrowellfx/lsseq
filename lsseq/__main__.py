# 3-Clause BSD License
# 
# Copyright (c) 2008-2021, James Philip Rowell,
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
import time
from operator import itemgetter
import seqLister

VERSION = "2.4.0"

CACHE_EXT = ["ass", "dshd", "fur", "obj", "srf", "bgeo", "ifd", "vdb",
    "bgeo.sc", "bgeo.gz", "ifd.sc", "ifd.gz", "vdb.sc", "vdb.gz"]
MOV_EXT = ["avi", "mov", "mp4", "mpg", "wmv"]
IMAGE_EXT = ["alpha", "als", "anim", "bmp", "btf", "bw", "cin",
    "dib", "dpx", "exr", "gfa", "gif", "giff", "icon", "iff", "img",
    "int", "inta", "jpe", "jpeg", "jpg", "JPEG", "JPG", "mask",
    "matte", "nef", "NEF", "pct", "pct1", "pct2", "pdb", "pdd",
    "pic", "piclc", "picnc", "pict", "pix", "png", "psb", "psd",
    "rat", "raw", "rgb", "rgba", "rle", "rw2", "sgi", "tga", "tif",
    "tiff", "tpic"]

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
    global IMAGE_EXT
    global CACHE_EXT

    fileComponents = filename.split(".")

    # A file with no extension.
    #
    if len(fileComponents) <= 1 :
        return fileComponents

    # Check for extensions with dot (for example, bgeo.sc, bgeo.g, or vdb.gz)
    # and join them before returning result.
    #
    if (".".join(fileComponents[-2:]) in IMAGE_EXT) \
	    or (".".join(fileComponents[-2:]) in CACHE_EXT) :

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

    global IMAGE_EXT
    global CACHE_EXT
    global LOOSE_SEP
    fileComponents = splitFileComponents(filename)

    # A file with no extension.
    #
    if len(fileComponents) <= 1 :
        return []

    # Test if image or cache sequence.
    #
    if (fileComponents[-1] in IMAGE_EXT) or (fileComponents[-1] in CACHE_EXT) :

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
    global MOV_EXT
    fileComponents = filename.split(".")

    return len(fileComponents) > 1 \
        and MOV_EXT.count(fileComponents[-1]) >= 1


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
    return splitName[-1] in CACHE_EXT

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

    fileComponents = splitImageName(filenameKey)

    missingFrames = []
    zeroFrames = []
    badFrames = []
    badPadFrames = []
    errFrames = []
    minFrame = frameList[0][FRAME_NUM]
    maxFrame = frameList[-1][FRAME_NUM]
    padding = 0 # Set below, created here for scope.

    # Calculate padding.
    #
    # Padding can be calculated from looking at the smallest
    # non-negative integer, or if ALL are negative, then the largest
    # negative integer. Since 1-padding and 2-padding are the same
    # for negative numbers, then it it doesn't matter which one we
    # choose, so we leave it at 2.
    #
    # See example: expandseq --pad 3 ' -11-11',
    #         and: expandseq --pad 2 ' -11-11'
    # 
    if minFrame >= 0 :
        padding = frameList[0][FRAME_PADDING]
    elif maxFrame < 0 :
        padding = frameList[-1][FRAME_PADDING]
    else :
        # Find smallest non-negative frame number.
        #
        i = 0
        while frameList[i][FRAME_NUM] < 0 :
            i += 1
        padding = frameList[i][FRAME_PADDING]

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
        if args.showMissing or args.showZero or args.showBad or args.showBadPadding :
            i = minFrame
            while i <= maxFrame :
                iMissing = False
                currFrameData = frameList[0]
                if i != currFrameData[FRAME_NUM] :
                    iMissing = True
                    if args.showMissing :
                        missingFrames.append(i)
                else :
                    frameList.pop(0)

                if not iMissing and (args.showZero or args.showBad or args.showBadPadding) :

                    if currFrameData[FRAME_MTIME] == FRAME_BROKENLINK :
                        if args.showZero :
                            zeroFrames.append(i)
                        elif args.showBad :
                            badFrames.append(i)
                        actualFilename = actualImageName(filenameKey, padding, i)
                        print( os.path.basename(sys.argv[0]), ": warning: ", actualFilename,
                            " is a broken soft link", sep='', file=sys.stderr)

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
            sys.stdout.write(traversedPath)

        if args.extremes :
            fileComponents[1] = formatStr % minFrame
        print(fileComponents[0], fileComponents[1], ".", fileComponents[2], sep='', end='')
        if minFrame != maxFrame and args.extremes :
            print()
            if fileComponents[0][0] != '/' :
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
# This fucntion assumes that if a directory "title" is needed
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
#                 used to print the directory "titles".
# 
def listSeqDir(dirContents, path, listSubDirs, args, traversedPath) :

    # Array indices for "timeList" used below.
    #
    DICTKEY = 0
    MTIME = 1

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
    # key for each entry.  Each entry is a list containing four-tuples-tuples,
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
        if args.byWhat == BY_SINGLE :
            extra_ls_options.append("-1")
        if args.byWhat == BY_COLUMNS :
            extra_ls_options.append("-C")
        if args.byWhat == BY_ROWS :
            extra_ls_options.append("-x")
        if args.sortByMTime :
            extra_ls_options.append("-t")
        if args.reverseListing :
            extra_ls_options.append("-r")
        extra_ls_options.append("--")
        lsCmd = ["ls", "-d"] + extra_ls_options + otherFiles
        sys.stdout.flush()
        subprocess.call(lsCmd)
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
                timeList.append((k, moviesDictionary[k]))

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
                timeList.append((k, time))

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
                timeList.append((k, time))

    if args.sortByMTime :
        timeList.sort(key=itemgetter(MTIME))
        # Note: ls -t prints newest first; ls -tr is newest last.
        if not args.reverseListing :
            timeList.reverse()
        for seq in timeList :
            if args.cutoffTime != None :
                if args.cutoffTime[0] == 'before' :
                    if seq[MTIME] >= args.cutoffTime[1] :
                        continue
                else : # Guaranteed to be 'since'
                    if seq[MTIME] <= args.cutoffTime[1] :
                        continue
            if isMovie(seq[DICTKEY]) :
                if args.prependPath != PATH_NOPREFIX :
                    sys.stdout.write(traversedPath)
                print(seq[DICTKEY])
                somethingWasPrinted = True
            elif isCache(seq[DICTKEY]) :
                cacheDictionary[seq[DICTKEY]].sort(key=itemgetter(FRAME_NUM))
                printSeq(seq[DICTKEY], cacheDictionary[seq[DICTKEY]], args, traversedPath)
                somethingWasPrinted = True
            else :
                imageDictionary[seq[DICTKEY]].sort(key=itemgetter(FRAME_NUM))
                printSeq(seq[DICTKEY], imageDictionary[seq[DICTKEY]], args, traversedPath)
                somethingWasPrinted = True
    elif args.cutoffTime != None :
        timeList.sort(key=itemgetter(DICTKEY))
        # Note: ls -t prints newest first; ls -tr is newest last.
        if not args.reverseListing :
            timeList.reverse()
        for seq in timeList :
            if args.cutoffTime[0] == 'before' :
                if seq[MTIME] >= args.cutoffTime[1] :
                    continue
            else : # Guaranteed to be 'since'
                if seq[MTIME] <= args.cutoffTime[1] :
                    continue
            if isMovie(seq[DICTKEY]) :
                if args.prependPath != PATH_NOPREFIX :
                    sys.stdout.write(traversedPath)
                print(seq[DICTKEY])
                somethingWasPrinted = True
            elif isCache(seq[DICTKEY]) :
                cacheDictionary[seq[DICTKEY]].sort(key=itemgetter(FRAME_NUM))
                printSeq(seq[DICTKEY], cacheDictionary[seq[DICTKEY]], args, traversedPath)
                somethingWasPrinted = True
            else :
                imageDictionary[seq[DICTKEY]].sort(key=itemgetter(FRAME_NUM))
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
                cacheDictionary[k].sort(key=itemgetter(FRAME_NUM))
                printSeq(k, cacheDictionary[k], args, traversedPath)
                somethingWasPrinted = True
            else :
                imageDictionary[k].sort(key=itemgetter(FRAME_NUM))
                printSeq(k, imageDictionary[k], args, traversedPath)
                somethingWasPrinted = True

    # lsseq - the contents of any subdirectories if need be.
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

    global IMAGE_EXT
    global MOV_EXT
    global CACHE_EXT
    global PATH_ABS
    global PATH_REL
    global LIST_ALLFILES
    global LIST_ONLYSEQS
    global LIST_ONLYIMGS
    global LIST_ONLYMOVS
    global LIST_ONLYCACHES

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
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
            List directory contents (akin to /bin/ls) while condensing image
            sequences to one entry each. Filenames that are part of image
            sequences are assumed to be of the form:

                <descriptiveName>.<frameNum>.<imgExtension>

            where <imgExtension> is drawn from a default list of image extensions
            (see option -i) or they can be set with the environment variable
            OIC_IMAGE_EXTENSION=exr:jpg:tif (for example).  Similarly, there is an
            OIC_MOV_EXTENSION environment variable for movie file extensions and
            OIC_CACHE_EXTENSION for caches and other miscellaneous sequences.

            %(prog)s will first list all non-image-sequence files followed by the
            list of image sequences as such:

                $ %(prog)s
                [output of /bin/ls minus image sequences]
                [list of images sequences]
            '''),
        usage="%(prog)s [OPTION]... [FILE]...")

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
    p.add_argument("--extremes", "-e", action="store_true",
        dest="extremes", default=False,
        help="only list the first and last image on a separate line each. \
        This option implies --prependPathAbs (unless --prependPathRel is \
        explicitly specified) and --onlySequences")
    p.add_argument("--imgExt", "-i", action="store_true",
        dest="printImgExtensions", default=False,
        help="print list of image, cache and movie file extensions and exit")
    p.add_argument("--looseNumSeparator", "-l", action="store_false",
        dest="strictSeparator",
        help="allow the use of '_' (underscore), in addition to '.' (dot) \
            as a separator between the descriptiveName and frameNumber when \
            looking to interpret filenames as \
            image sequences. i.e., <descriptiveName>_<frameNum>.<imgExtension> \
            (also see --strictNumSeparator)")
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
    p.add_argument("--strictNumSeparator", "-s", action="store_true",
        dest="strictSeparator", default=True,
        help="strictly enforce the use of '.' (dot) as a separator between the \
            descriptiveName and frameNumber when looking to interpret filenames as \
            image sequences. i.e., <descriptiveName>.<frameNum>.<imgExtension> \
            (also see --looseNumSeparator) [default]")
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
    p.add_argument("--time", action="store", type=str,
        dest="timeCompare",
        help="which frame in the sequence to use to compare times \
        between sequences when sorting by time. The possible values \
        for 'FRAME_AGE' are 'oldest', 'median' and 'newest' \
        [default: 'newest']", metavar="FRAME_AGE", default="newest",
        choices=("oldest", "median", "newest"))
    p.add_argument("-t", action="store_true",
        dest="sortByMTime", default=False,
        help="sort by modification time, the default comparison \
        time is between the most recently modified (newest) frames \
        in each sequence. (see --time) (see ls(1))")
    p.add_argument("--onlyShow", action="store", type=str, nargs=2,
        dest="cutoffTime",
        help="where TENSE is either 'before' or 'since'; only list sequences \
        up to (and including) or after (and including) the time specified. The --time argument \
        specifies which frame to use for the cutoff comparison",
        metavar=("TENSE", "[[CC]YY]MMDDhhmm[.ss]"))

    p.add_argument("files", metavar="FILE", nargs="*",
        help="file names")

    args = p.parse_args()

    tmpExt = os.getenv("OIC_IMAGE_EXTENSION")
    if tmpExt != None and tmpExt != "" :
        tmpExtList = tmpExt.split(":")
    else :
        tmpExtList = IMAGE_EXT
    tmpExtList.sort()
    IMAGE_EXT = []
    for e in tmpExtList :
        IMAGE_EXT.append(e)

    tmpExt = os.getenv("OIC_MOV_EXTENSION")
    if tmpExt != None and tmpExt != "" :
        tmpExtList = tmpExt.split(":")
    else :
        tmpExtList = MOV_EXT
    tmpExtList.sort()
    MOV_EXT = []
    for e in tmpExtList :
        MOV_EXT.append(e)

    tmpExt = os.getenv("OIC_CACHE_EXTENSION")
    if tmpExt != None and tmpExt != "" :
        tmpExtList = tmpExt.split(":")
    else :
        tmpExtList = CACHE_EXT
    tmpExtList.sort()
    CACHE_EXT = []
    for e in tmpExtList :
        CACHE_EXT.append(e)

    if args.printImgExtensions :
        extList = ":".join(IMAGE_EXT)
        print("OIC_IMAGE_EXTENSION:", extList)
        extList = ":".join(MOV_EXT)
        print("OIC_MOV_EXTENSION:", extList)
        extList = ":".join(CACHE_EXT)
        print("OIC_CACHE_EXTENSION:", extList)
        sys.exit(0)

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
        args.cutoffTime[0] = args.cutoffTime[0].lower()
        if (args.cutoffTime[0] != 'before') and (args.cutoffTime[0] != 'since') :
            print(os.path.basename(sys.argv[0]),
                ": error: argument --onlyShow: TENSE must be 'since' or 'before'",
                file=sys.stderr, sep='')
            sys.exit(1)
        timeSpec = args.cutoffTime[1].split('.')
        if len(timeSpec) <= 2 :
            if   len(timeSpec[0]) == 12 :
                timeFormat = "%Y%m%d%H%M"
            elif len(timeSpec[0]) == 10 :
                timeFormat = "%y%m%d%H%M"
            elif len(timeSpec[0]) == 8 :
                timeFormat = "%m%d%H%M"
            else :
                print(os.path.basename(sys.argv[0]),
                    ": error: argument --onlyShow: the time must be of the form [[CC]YY]MMDDhhmm[.ss]",
                    file=sys.stderr, sep='')
                sys.exit(1)
        if len(timeSpec) == 2 :
            timeFormat += ".%S"

        try :
            timeData=time.strptime(args.cutoffTime[1], timeFormat)
        except ValueError :
            print(os.path.basename(sys.argv[0]),
                ": error: argument --onlyShow: the time must be of the form [[CC]YY]MMDDhhmm[.ss]",
                file=sys.stderr, sep='')
            sys.exit(1)

        args.cutoffTime[1] = int(time.mktime(timeData)) # Epoch time


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

if __name__ == '__main__' :
    main()
