#!/usr/bin/python3

import sys
from fast import Fast
from bakery import Bakery

if __name__ == "__main__":
    if len(sys.argv) == 3:
        num_of_threads, num_of_reqs = int(sys.argv[1]), int(sys.argv[2])
    else:
        num_of_threads, num_of_reqs = 3, 5 # defaults
    
    print("\nRunning Lamport's fast mutual exclusion algorithm")
    threads = [Fast(i) for i in range(1, num_of_threads+1)]
    Fast.setup(threads, num_of_reqs)
    Fast.start_all()
    
    # wait for all threads to die..
    for thread in threads:
        thread.join()
    
    print("\n\nRunning Lamport's bakery algorithm")
    threads = [Bakery(i) for i in range(1, num_of_threads+1)]
    Bakery.setup(threads, num_of_reqs )
    Bakery.start_all()
    
    # wait for all threads to die..
    for thread in threads:
        thread.join()
    
    print()
