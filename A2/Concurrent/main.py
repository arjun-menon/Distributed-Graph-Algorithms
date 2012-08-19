#!/usr/bin/python3

import sys, fast, bakery

if __name__ == "__main__":
    if len(sys.argv) == 3:
        num_of_threads, num_of_reqs = int(sys.argv[1]), int(sys.argv[2])
    else:
        num_of_threads, num_of_reqs = 3, 15 # defaults
    
    print("\nRunning Lamport's fast mutual exclusion algorithm")
    threads = [fast.Fast(i) for i in range(num_of_threads)]
    fast.setup(threads, num_of_reqs)
    fast.start()
    
    # wait for all threads to die..
    for thread in threads:
        thread.join()
    
    print("\n\nRunning Lamport's bakery algorithm")
    threads = [bakery.Bakery(i) for i in range(num_of_threads)]
    bakery.setup(threads, num_of_reqs )
    bakery.start()
    
    # wait for all threads to die..
    for thread in threads:
        thread.join()
    
    print()
