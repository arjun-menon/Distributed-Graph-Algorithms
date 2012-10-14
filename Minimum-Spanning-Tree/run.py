#!/usr/bin/python3

import sys
sys.path.append("..") # if DistAlgo is not installed, use the one in parent directory

from distalgo.runtime import *

sys.argv = [sys.argv[0], "MST.dis"] + sys.argv[1:]

libmain()
