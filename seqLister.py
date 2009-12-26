# Expands seqlist, which is a list of integers and or strings with the
# following format, into a list of integers:
# 
# individual frame numbers: 1, "4", 10, 12
#     -> yeilds 1, 4, 10, 12
# sequences of successive frame numbers: "1-4", "10-15"
#     -> yeilds 1, 2, 3, 4, 10, 11, 12, 13, 14, 15
# sequences of skipped frame numbers: "1-10x2", "20-60x10"
#     -> yeilds 1, 3, 5, 7, 9, 20, 30, 40, 50, 60
# reverse sequences work too: 5-1
#     -> yeilds 5, 4, 3, 2, 1
# 
# These formats may be listed in any order, but if a number has
# been listed once, it will not be listed again.
# 
# Eg. "0-16x8", "0-16x2"
#     -> yeilds 0, 8, 16, 2, 4, 6, 10, 12, 14
# 
# Anything that is not of the above format is simply ingnored.
#
# If you want the list to be sorted, then sort the returned list of numbers.
# 
def expandSeq(seqList) :

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
	seqItem = seqItem.replace(" ", "")
	seqItem = seqItem.replace("	", "")
	seqItemList = seqItem.split("-")

	if "x" in seqItemList[-1] :
	    lastItem = seqItemList[-1].split("x")
	    if len(lastItem) != 2 :
		continue
	    if not (lastItem[0].isdigit() and lastItem[1].isdigit()) :
		continue
	    stepValue = int(lastItem[1])
	    seqItemList[-1] = lastItem[0]

	if seqItemList[0] == "" :
	    seqItemList.pop(0)
	    if len(seqItemList) == 0:
		continue
	    if not seqItemList[0].isdigit() :
		continue
	    seqItemList[0] = -1 * int(seqItemList[0])
	elif seqItemList[0].isdigit() :
	    seqItemList[0] = int(seqItemList[0])
	else :
	    continue

	if len(seqItemList) == 1 : # Was just string with one number in it.
	    if seqItemList[0] not in resultList :
		resultList.append(seqItemList[0])
	    continue

	if seqItemList[1] == "" :
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

	if len(seqItemList) != 2 : 
	    continue # Should only be exactly two entries at this point.

	if seqItemList[0] == seqItemList[1] :
	    if seqItemList[0] not in resultList :
		resultList.append(seqItemList[0])
	    continue

	if seqItemList[0] < seqItemList[1] :
	    frameNum = seqItemList[0]
	    while frameNum <= seqItemList[1] :
		if frameNum not in resultList :
		    resultList.append(frameNum)
		frameNum =  frameNum + stepValue
	else :
	    frameNum = seqItemList[0]
	    while frameNum >= seqItemList[1] :
		if frameNum not in resultList :
		    resultList.append(frameNum)
		frameNum =  frameNum - stepValue


    return resultList
