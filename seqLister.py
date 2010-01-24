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
    #     -> yeilds [1, 4, 10, 15]
    # sequences of successive frame numbers: ["1-4", "10-15"]
    #     -> yeilds [1, 2, 3, 4, 10, 11, 12, 13, 14, 15]
    # sequences of skipped frame numbers: ["1-10x2", "20-60x10"]
    #     -> yeilds [1, 3, 5, 7, 9, 20, 30, 40, 50, 60]
    # reverse sequences work too: ["5-1"]
    #     -> yeilds [5, 4, 3, 2, 1]
    # 
    # These formats may be listed in any order, but if a number has
    # been listed once, it will not be listed again.
    # 
    # Eg. ["0-16x8", "0-16x2"]
    #     -> yeilds [0, 8, 16, 2, 4, 6, 10, 12, 14]
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
	    continue

	if seqItemList[0] < seqItemList[1] : # Counting up.
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


def compressSeq(seqList) :

    if len(seqList) == 0 :
	return []
    if  len(seqList) == 1 :
	return [str(seqList[0])]

    # At this point - guaranteed that len(seqList) > 1

    seqList.sort()
    resultList = []
    gapList = []
    i = 1
    while i < len(seqList) :
	gapList.append(seqList[i] - seqList[i-1])
	resultList.append(str(seqList[i]))
	i = i + 1

    return gapList
