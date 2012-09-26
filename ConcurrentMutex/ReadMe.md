Concurrent Mutex algorithms
---------------------------
This is an implementation of Lamport's fast mutual exclusion and bakery 
algorithms for atomizing access to crucial resources. The purpose of 
both algorithms are to ensure that a segment of code known as the 
**critical section** does _not_ get executed concurrently.

The module `fast.py`   implements Lamport's fast mutex algorithm and 
the module `bakery.py` implements Lamport's bakery algorithm.

The module `auxiliary.py` defines three important functions: `random_distribution`, `await` and `default_task`.

`random_distribution` is a function that takes a number of threads, 
and a total number of requests amd returns a list L where L[i] 
epresents a number of requests (randomly assigned) to thread i.

`await(func)` takes a function as argument, busy waits until 
the return value of `func()` becomes True. 

`default_task()` defines the default task to be executed while 
inside the critical section. Currently it is a CPU hog that 
computes prime numbers up to an "nth" value specified inside the 
module. The prime number calculator was lifted from Stack Overflow.

`main.py` starts up n threads and m requests per thread, n and m being 
passed as command line arguments. It runs both tests & terminates. 
