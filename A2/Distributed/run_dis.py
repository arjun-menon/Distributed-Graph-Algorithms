#!/usr/bin/python3

'''
Runs a DistAlgo (.dis) program
'''

from distalgo.runtime import *

import sys
sys.argv = [ sys.argv[0], "RAtoken.dis" ]

libmain()