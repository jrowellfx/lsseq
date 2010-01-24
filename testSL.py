import seqLister
print "Testing expandSeq()"
print seqLister.expandSeq([1, "4", 10, 15])
print seqLister.expandSeq(["1-4", "10-15"])
print seqLister.expandSeq(["1-10x2", "20-60x10"])
print seqLister.expandSeq(["5-1"])
print seqLister.expandSeq(["0-16x8", "0-16x2"])
print ""
print "Testing compressSeq()"
print seqLister.compressSeq([])
print seqLister.compressSeq([1])
print seqLister.compressSeq(["2"])
print seqLister.compressSeq([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
print seqLister.compressSeq([2, 1, 3, 7, 8, 4, 5, 6, 9, 10])
