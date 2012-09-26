#!/usr/bin/python3

'''
This was a file used during development. You can ignore this file.

To run the DistAlgo programs, just use:

	python3 -m distalgo.runtime RAtoken.dis

	python3 -m distalgo.runtime SKtoken.dis

Disclaimer: For some strange reaosn this file doesn't work properly when run from command line. I used 
Eclipse during  development, and it worked fine in it. Might have something to do with PYTHONPATH...
'''

import sys
from distalgo.runtime import *

RA, SK = 'RA', 'SK'

prog = SK

if len(sys.argv) > 1:
	prog = sys.argv[1]

if prog == RA:
	sys.argv = [ sys.argv[0], "RAtoken.dis" ]
	libmain()

elif prog == SK:
	sys.argv = [ sys.argv[0], "SKtoken.dis" ]
	libmain()

else:
	print("Command-line argument must be 'RA' or 'SK'. (Not %s)" % sys.argv[1])
	sys.exit(1)
