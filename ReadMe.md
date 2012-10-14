Distributed Graph Algorithms in DistAlgo
----------------------------------------
This repository contains the implementations of a some *distributed* graph algorithms as well as two token-based mutex algorithms in ***DistAlgo***. DistAlgo is a superset of Python that adds special constructs to Python for specifying distributed algorithms in a high-level and succint manner. DistAlgo programs get compiled to portable Python 3 code. DistAlgo was developed at the [Department of Computer Science](http://www.cs.sunysb.edu/) in Stony Brook University. It is used in the instruction of some graduate-level such as [CSE 535 Asynchronous Systems](http://www.cs.stonybrook.edu/~liu/cse535/) by [Annie Liu](http://www.cs.sunysb.edu/~liu/) and [CSE 594 Distributed Systems](http://www.cs.sunysb.edu/~stoller/cse594/) by [Scott Stoller](http://www.cs.sunysb.edu/~stoller/).

### The Distributed Graph Algorithms
The following distributed graph algorithms that have implemented using **DistAlgo-0.2**:

1. [Minimum Spanning Tree](https://github.com/arjungmenon/Distributed-Graph-Algorithms/tree/master/Minimum-Spanning-Tree)
2. [Maximal Independent Set](https://github.com/arjungmenon/Distributed-Graph-Algorithms/tree/master/Maximal-Independent-Set)
3. [Breadth First Search](https://github.com/arjungmenon/Distributed-Graph-Algorithms/tree/master/Breadth-First-Search)
4. [Shortest Path](https://github.com/arjungmenon/Distributed-Graph-Algorithms/tree/master/ShortestPath)

The subdirectory of each algorithm contains a relevant ***ReadMe*** file that describes the algorithm in detail with specific information about its implementation, limitations, etc.

#### Code Length
Lines of Code have never really been a good statistic on how long it took to write a piece of code. In addition, certain languages are more dense than others. For example this single statement turns a graph file into a list of NetworkX edges: `( edge(ed.split()[0], ed.split()[1], int(ed.split()[2])) for ed in (e.strip() for e in f.readlines() if e.strip() != "") if len(ed.split()) == 3 )`. It would however taken a lot more code in an arcance language like Java.

However, I still think the *lines of code* would be an interesting statistic, so I'm providing it below:



The numbers were generated using `cloc`, a popular Perl utility for counting lines of code. There is some repition/shared code in each algorithm -- probabably around 100 lines in each.

In Fred Brooke's mythical man-moth he mentions 

#### Note about References
All references have been hyperlinked in-place using [Markdown's link syntax](http://daringfireball.net/projects/markdown/syntax#link).

### Other
[Ricart-Agrawala's and Suzuki-Kasami's token-based distributed mutex algorithms](https://github.com/arjungmenon/Distributed-Graph-Algorithms/tree/master/DistributedMutex) have also been been implemented in DistAlgo-0.2. In addition, [Lamport's fast mutual exclusion and bakery algorithms](https://github.com/arjungmenon/Distributed-Graph-Algorithms/tree/master/ConcurrentMutex) have been implemented using the built-in Python library `threading`.
