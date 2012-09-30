#!/usr/bin/python3

import sys
from distalgo.runtime import *

if len(sys.argv) == 1:
	sys.argv = [sys.argv[0], "MST.dis"]

libmain()
