Distributed Graph Algorithms in DistAlgo
----------------------------------------
This repository contains the implementations of a some _distributed_ graph algorithms as well as two token-based mutex algorithms in ***DistAlgo***. DistAlgo is a superset of Python that adds special constructs to Python for specifying distributed algorithms in a high-level and succint manner. DistAlgo programs get compiled to portable Python 3 code. DistAlgo was developed at the [Department of Computer Science](http://www.cs.sunysb.edu/) in Stony Brook University. It is used in the instruction of some graduate-level such as [CSE 535 Asynchronous Systems](http://www.cs.stonybrook.edu/~liu/cse535/) by [Annie Liu](http://www.cs.sunysb.edu/~liu/) and [CSE 594 Distributed Systems](http://www.cs.sunysb.edu/~stoller/cse594/) by [Scott Stoller](http://www.cs.sunysb.edu/~stoller/).

#### Distributed Graph Algorithms
The following distributed graph algorithms that have implemented using **DistAlgo-0.2**:
1. [Minimum Spanning Tree](https://github.com/arjungmenon/Distributed-Graph-Algorithms/tree/master/Minimum-Spanning-Tree)
2. [Maximal Independent Set](https://github.com/arjungmenon/Distributed-Graph-Algorithms/tree/master/Maximal-Independent-Set)
3. [Breadth First Search](https://github.com/arjungmenon/Distributed-Graph-Algorithms/tree/master/Breadth-First-Search)
4. [Shortest Path](https://github.com/arjungmenon/Distributed-Graph-Algorithms/tree/master/ShortestPath)

### Other
[Ricart-Agrawala's and Suzuki-Kasami's token-based distributed mutex algorithms](https://github.com/arjungmenon/Distributed-Graph-Algorithms/tree/master/DistributedMutex) have also been been implemented in DistAlgo-0.2. In addition, [Lamport's fast mutual exclusion and bakery algorithms](https://github.com/arjungmenon/Distributed-Graph-Algorithms/tree/master/ConcurrentMutex) have been implemented using the built-in Python library `threading`.
