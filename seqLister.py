# Copyright (c) 2008-2010, James Philip Rowell,
# Orange Imagination & Concepts, Inc.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
#   - Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   - Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#   - Neither the name "Orange Imagination & Concepts, Inc." nor the
#     names of its contributors may be used to endorse or promote
#     products derived from this software without specific prior written
#     permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


# seqLister module - used for expanding and compressing ranges of
# frame numbers to/from a common format to describe such ranges.


def expandSeq(seqList) :
    #
    # Expands seqlist, which is a list of integers and or strings with the
    # following format, into a list of integers:
    # 
    # individual frame numbers: [1, "4", 10, 15]
    #     yeilds -> [1, 4, 10, 15]
    # sequences of successive frame numbers: ["1-4", "10-15"]
    #     yeilds -> [1, 2, 3, 4, 10, 11, 12, 13, 14, 15]
    # sequences of skipped frame numbers: ["1-10x2", "20-60x10"]
    #     yeilds -> [1, 3, 5, 7, 9, 20, 30, 40, 50, 60]
    # reverse sequences work too: ["5-1"]
    #     yeilds -> [5, 4, 3, 2, 1]
    # 
    # These formats may be listed in any order, but if a number has
    # been listed once, it will not be listed again.
    # 
    # Eg. ["0-16x8", "0-16x2"]
    #     yeilds -> [0, 8, 16, 2, 4, 6, 10, 12, 14]
    # 
    # Anything that is not of the above format is simply ingnored.
    #
    # If you want the list to be sorted, then sort the returned
    # list of numbers.

    if not isinstance(seqList, list) :
	return []

    resultList = []
    for seqItem in seqList :
	if not (isinstance(seqItem, int) or isinstance(seqItem, str)) :
	    # Discard item and continue to next one
	    continue

	if isinstance(seqItem, int) :
	    if seqItem not in resultList :
		resultList.append(seqItem)
	    continue

	stepValue = 1
	seqItem = seqItem.replace(" ", "") # Strip all whitespace.
	seqItem = seqItem.replace("	", "")

	# No stepping by negative numbers - step back by reversing start/end
	seqItem = seqItem.replace("x-", "x")

	seqItemList = seqItem.split("-") # might be range or neg number.

	if "x" in seqItemList[-1] :
	    lastItem = seqItemList[-1].split("x")
	    if len(lastItem) != 2 :
		continue
	    if not lastItem[1].isdigit() :
		continue
	    stepValue = int(lastItem[1])
	    seqItemList[-1] = lastItem[0] # Stick back in list minux "xN" part

	if seqItemList[0] == "" : # Means there was leading minus sign.
	    seqItemList.pop(0)
	    if len(seqItemList) == 0:
		continue
	    if not seqItemList[0].isdigit() :
		continue
	    seqItemList[0] = -1 * int(seqItemList[0]) # Repace first entry...
	elif seqItemList[0].isdigit() :
	    seqItemList[0] = int(seqItemList[0]) #...with an ingeter.
	else :
	    continue

	if len(seqItemList) == 1 : # Was just string with one number in it.
	    if seqItemList[0] not in resultList :
		resultList.append(seqItemList[0])
	    continue

	if seqItemList[1] == "" : # Same as above for next entry.
	    seqItemList.pop(1)
	    if len(seqItemList) == 1:
		continue
	    if not seqItemList[1].isdigit() :
		continue
	    seqItemList[1] = -1 * int(seqItemList[1])
	elif seqItemList[1].isdigit() :
	    seqItemList[1] = int(seqItemList[1])
	else :
	    continue

	# Should only be exactly two entries at this point.
	if len(seqItemList) != 2 : 
	    continue

	# Ummm - dumb but why not? list from n to n, i.e., one number.
	if seqItemList[0] == seqItemList[1] :
	    if seqItemList[0] not in resultList :
		resultList.append(seqItemList[0])
	elif seqItemList[0] < seqItemList[1] : # Counting up.
	    frameNum = seqItemList[0]
	    while frameNum <= seqItemList[1] :
		if frameNum not in resultList :
		    resultList.append(frameNum)
		frameNum =  frameNum + stepValue
	else : # Counting down.
	    frameNum = seqItemList[0]
	    while frameNum >= seqItemList[1] :
		if frameNum not in resultList :
		    resultList.append(frameNum)
		frameNum =  frameNum - stepValue

    return resultList

class gapRun :
    def __init__(self, seqLen, startInd, gapSize, isCorrected=False) :
        self.seqLen = seqLen
        self.startInd = startInd
        self.gapSize = gapSize
        self.isCorrected = isCorrected

# [seqLen, gapSize, index])
def cmpFunc(x, y) :
    # There is only one entry with zero
    # gap-length, it is always "smallest"
    if x[1] == 0 :
	return -1
    elif y[1] == 0 :
	return 1
    if x[0] == y[0] :
	if x[1] == y[1] :
	    if x[2] == y[2] : # Impossible
		return 0
	    elif x[2] < y[2] : # Reverses based on index.
		return 1
	    else :
		return -1
	elif x[1] < y[1] : # Reverses based on gapsize
	    return 1
	else :
	    return -1
    elif x[0] < y[0] :
	return -1
    else :
	return 1

def compressSeq(seqList, pad=1) :

    # Turn seqList into all integers and throw away invalid entries
    #
    tmpSeqList = seqList
    seqList = []
    for n in tmpSeqList :
	if isinstance(n, int) :
	    seqList.append(int(n))
	if isinstance(n, str) :
	    if n.isdigit() :
		seqList.append(int(n))
	    elif n[0] == "-" and n[1:].isdigit() :
		seqList.append(-1 * int(n))

    if len(seqList) == 0 : # Take care of 1st trivial case
	return []

    # Remove duplicates
    #
    seqList.sort()
    tmpSeqList = seqList
    seqList = []
    seqList.append(tmpSeqList[0])
    tmpSeqList.pop(0)
    for n in tmpSeqList :
	if n != seqList[-1] :
	    seqList.append(n)

    formatStr = "%0" + str(pad) + "d"

    if len(seqList) == 1 : # Take care of second trivial case.
	return [formatStr % seqList[0]]

    # At this point - guaranteed that len(seqList) > 1

    gapList = []
    i = 1
    while i < len(seqList) : # Record gaps between frame #'s
	gapList.append(seqList[i] - seqList[i-1])
	i += 1

    # Count lengths of similar "gaps".
    i = 0 
    currentGap = 0 # Impossible - good starting point.
    gapRunList = []
    while i < len(gapList) :
	if gapList[i] != currentGap :
	    currentGap = gapList[i]
	    gapRunList.append(gapRun(1, i, currentGap))
	else :
	    gapRunList[-1].seqLen += 1
	i += 1
    gapRunList.append(gapRun(1, i, 0)) # Add entry for last number in seqList (note zero gapSize)

    # Sorts the runs of gaps into largest to smallest runs, and the larger runs try
    # to steal from the next runs first-frame if possible.
    #
    while True :
	i = 0
	gapRunSorted = []
	for run in gapRunList :
	    if not run.isCorrected :
		gapRunSorted.append([run.seqLen, run.gapSize, i])
	    i += 1
	gapRunSorted.sort(cmp=cmpFunc, reverse=True)
	runInd = gapRunSorted[0][2] # This is the "largest" run currently.

	if gapRunList[runInd].gapSize == 0 : # Means we've hit the end and we're done.
	    break

	gapRunList[runInd].isCorrected = True

	# Steal from next sequence if possible.
	run = gapRunList[runInd]
	nextRun = gapRunList[runInd+1]
	if not nextRun.isCorrected : # Means it was bigger than this one and we can't steal from it.
	    # This next test just avoids the case of making random
	    # sequences of numbers into little two entry lists with
	    # large gaps.
	    #
	    if not (run.seqLen == 1 and run.gapSize > 1) :
		gapRunList[runInd].seqLen += 1
		gapRunList[runInd+1].seqLen -= 1
		gapRunList[runInd+1].startInd += 1

    # Now that we've gone through once, run through again, now for each run
    # if the gapSize is smaller than the NEXT run, AND the seqLen is only one LESS than
    # the seqLength of the next run, steal the first entry from the next run.
    i = 0
    while i < len(gapRunList)-1 :
	if not (gapRunList[i].seqLen == 1 and gapRunList[i].gapSize > 1) \
	    and (gapRunList[i].gapSize < gapRunList[i+1].gapSize) \
	    and (gapRunList[i].seqLen == gapRunList[i+1].seqLen - 1) :
	    gapRunList[i].seqLen += 1
	    gapRunList[i+1].seqLen -= 1
	    gapRunList[i+1].startInd += 1
	i += 1

    compressList = []

    for run in gapRunList :
	if run.seqLen == 0 :
	    continue

	if run.seqLen == 1 :
	    compressList.append(formatStr % seqList[run.startInd])
	    continue

	# Don't print out this case as a range, but as two separate entries.
	#
	if run.seqLen == 2 and run.gapSize > 1:
	    compressList.append(formatStr % seqList[run.startInd])
	    compressList.append(formatStr % seqList[run.startInd+1])
	    continue

	firstFrame = seqList[run.startInd]
	lastFrame = seqList[run.startInd + run.seqLen - 1]
	gap = run.gapSize
	compressList.append(formatStr % firstFrame +"-"+ formatStr % lastFrame)
	if gap > 1 :
	    compressList[-1] = compressList[-1] + "x" + str(gap)

    return compressList
