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

sys.argv = [ sys.argv[0], "RAtoken.dis" ]
#libmain()

sys.argv = [ sys.argv[0], "SKtoken.dis" ]
libmain()

