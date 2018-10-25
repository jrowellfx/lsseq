#!/usr/bin/python2.7

# BSD 3-Clause License
# 
# Copyright (c) 2008-2018, James Philip Rowell,
# Alpha Eleven Incorporated
# www.alpha-eleven.com
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#   - Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
#   - Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#
#   - Neither the name of "Alpha Eleven, Inc."  nor the names of its
#     contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
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

import os
import sys
import math
from operator import itemgetter

# WIP - util for helping determine "bad" frames based on file sizes
# deviation from a rolling avg of frame sizes.
#
def rollingAvg(list, window) :

    # window must be a positive integer.
    assert window > 0

    # The rolling avg is (list[i-window] + ... + list[i+window])/window
    # i.e.; the actual window size is (2*window + 1) in length.

    result = [] # List of [ [rollingAvg, stddev], ... ]
    list_len = len(list)
    if list_len == 0 :
	return result
    elif list_len == 1 :
	result.append([list[0], 0])
	return result
    else :
	i = 0
	listSquared = []
	while i < list_len :
	    listSquared.append(list[i] * list[i])
	    i += 1

	start = 0
	end = window
	if end >= list_len - 1 :
	    # List is so short that window extends beyond 
	    # or touches the end already.
	    end = list_len - 1
	    touchEnd = True
	winLen = end + 1
	winLenSq = winLen * winLen
	runningSum = 0
	runningSumSq = 0
	i = 0
	while i <= end :
	    runningSum += list[i]
	    runningSumSq += listSquared[i]
	    i += 1
	mean = float(runningSum) / winLen
	stdev = math.sqrt((float(runningSumSq)/winLen) - (float(runningSum * runningSum)/winLenSq))
	result.append([mean, stdev])

	j = 1
	while j < list_len :
	    start = j - window
	    if start <= 0 :
		start = 0
	    else :
		runningSum -= list[start-1]
		runningSumSq -= listSquared[start-1]
	    end = j + window
	    if end >= list_len:
		end = list_len -1
	    else :
		runningSum += list[end]
		runningSumSq += listSquared[end]
	    winLen = end - start + 1
	    winLenSq = winLen * winLen
	    mean = float(runningSum) / winLen
	    stdev = math.sqrt((runningSumSq/winLen) - ((runningSum * runningSum)/winLenSq))
	    result.append([mean, stdev])

	    j += 1

	return result
