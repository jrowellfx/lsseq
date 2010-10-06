import seqLister
print "Testing expandSeq()"
print seqLister.expandSeq([1, "004", 10, 15])
print seqLister.expandSeq(["1-4", "010-015"])
print seqLister.expandSeq(["1-10x2", "20-60x10"])
print seqLister.expandSeq(["5-1"])
print seqLister.expandSeq(["5--2"])
print seqLister.expandSeq(["10--10x2"])
print seqLister.expandSeq(["10--10x-2"])
print seqLister.expandSeq(["0-16x8", "0-16x2"])
print seqLister.expandSeq(["0-99x9"])
print seqLister.expandSeq(["1-0100x9"])
print seqLister.expandSeq(["0-99x10"])
print seqLister.expandSeq(["0-9", "20-40x2"])
print seqLister.expandSeq(["0-6", "6-14x2", "14-70x10"])
print seqLister.expandSeq(["0-64x64", "0-64x32", "0-64x16", "0-64x8", "0-64x4", "0-64x2", "0-64"])
print seqLister.expandSeq(["1-6-12"]) # invalid
print seqLister.expandSeq(["1---6"]) # invalid
print seqLister.expandSeq(["1-6xa"]) # invalid
print seqLister.expandSeq(["1-6x2-"]) # invalid
print seqLister.expandSeq(["a-b"]) # invalid
print seqLister.expandSeq(["10--10x--2"]) # invalid
print ""
print "Testing compressSeq()"
print seqLister.compressSeq([])
print seqLister.compressSeq([1])
print seqLister.compressSeq(["2"], pad=4)
print seqLister.compressSeq([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
print seqLister.compressSeq([2, 1, 3, 7, 8, 4, 5, 6, 9, 10])
print seqLister.compressSeq([0, 8, 16, 2, 4, 6, 10, 12, 14])
print seqLister.compressSeq([0, 9, 18, 27, 36, 45, 54, 63, 72, 81, 90, 99])
print seqLister.compressSeq([1, 10, 19, 28, 37, 46, 55, 64, 73, 82, 91, 100])
print seqLister.compressSeq([0, 10, 20, 30, 40, 50, 60, 70, 80, 90])
print seqLister.compressSeq([1, 1, 1])
print seqLister.compressSeq([1, 1, 1, 2, 3])
print seqLister.compressSeq([1, 1, 1, 3, 3, 5, 5, 5])
print seqLister.compressSeq([1, 2])
print seqLister.compressSeq([1, 5])
print seqLister.compressSeq([1, 2, 5, 6, 9, 10])
print seqLister.compressSeq([1, 5, 13])

tmpList = seqLister.expandSeq(["0-100x2", 51])
print seqLister.compressSeq(tmpList)

tmpList = seqLister.expandSeq(["0-100x2", 51, 101, 102])
print seqLister.compressSeq(tmpList)

tmpList = seqLister.expandSeq(["1-5", "7-15x2"])
print seqLister.compressSeq(tmpList)

tmpList = seqLister.expandSeq(["1-5", "7-15x2", "20-100x5"])
print seqLister.compressSeq(tmpList)

tmpList = seqLister.expandSeq(["2-10x2", "14-30x4", "35-100x5"])
print seqLister.compressSeq(tmpList)

print seqLister.compressSeq([1, 2, 3, 4, 6, 8, 10])
print seqLister.compressSeq([1, 2, 3, 4, 6, 8])
print seqLister.compressSeq([1, 2, 3, 4, 6, 8, 10, 12, 13, 14, 15, 16])
print seqLister.compressSeq([1, 2, 3, 4, 6, 8, 10, 12, 13, 14, 15])
print seqLister.compressSeq([1, 2, 3, 4, 6, 8, 10, 11, 12])
print seqLister.compressSeq([1, 2, 3, 4, 6, 8, 10, 11])

print seqLister.compressSeq([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40])
print seqLister.compressSeq([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 13, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40])
print seqLister.compressSeq([0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 14, 24, 34, 44, 54, 64])
print seqLister.compressSeq([4, 5, 6, 8, 10, 12, 14, 24, 34, 44, 54, 64])
print seqLister.compressSeq([0, 64, 32, 16, 48, 8, 24, 40, 56, 4, 12, 20, 28, 36, 44, 52, 60, 2, 6, 10, 14, 18, 22, 26, 30, 34, 38, 42, 46, 50, 54, 58, 62, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49, 51], pad=2)
print seqLister.compressSeq([0, 64, 32, 16, 48, 8, 24, 40, 56, 4, 12, 20, 28, 36, 44, 52, 60, 2, 6, 10, 14, 18, 22, 26, 30, 34, 38, 42, 46, 50, 54, 58, 62, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21], pad=4)
print seqLister.compressSeq([0, 64, 32, 16, 48, 8, 24, 40, 56, 4, 12, 20, 28, 36, 44, 52, 60, 2, 6, 10, 14, 18, 22, 26, 30, 34, 38, 42], pad=4)

tmpList = seqLister.expandSeq(["5-400x5", "7-400x7", "11-400x11", "13-400x13"])
print seqLister.compressSeq(tmpList)

tmpList = seqLister.expandSeq(["5-400x5", "7-400x7", "11-400x11", "13-400x13", "17-400x17", "19-400x19"])
print seqLister.compressSeq(tmpList)

tmpList = seqLister.expandSeq(["5-400x5", "7-400x7", "11-400x11", "13-400x13", "17-400x17", "19-400x19", "23-400x23", "29-400x29", "31-400x31"])
print seqLister.compressSeq(tmpList)

tmpList = seqLister.expandSeq(["3-400x3", "5-400x5", "7-400x7", "11-400x11", "13-400x13", "17-400x17", "19-400x19", "23-400x23", "29-400x29", "31-400x31"])
print seqLister.compressSeq(tmpList)

tmpList = seqLister.expandSeq(["2-400x2", "3-400x3", "5-400x5", "7-400x7", "11-400x11", "13-400x13", "17-400x17", "19-400x19", "23-400x23", "29-400x29", "31-400x31"])
print seqLister.compressSeq(tmpList)

tmpList = seqLister.expandSeq(["2-400x2", "3-400x3", "5-400x5", "7-400x7", "11-400x11", "13-400x13", "17-400x17", "19-400x19", "23-400x23", "29-400x29", "31-400x31", "120-301"])
print seqLister.compressSeq(tmpList)
