Distributed Graph Algorithms in DistAlgo
----------------------------------------
This repository contains the implementations of a some *distributed* graph algorithms as well as two token-based mutex algorithms in *DistAlgo*. DistAlgo is a superset of Python that adds special constructs to Python for specifying distributed algorithms in a high-level and succint manner. DistAlgo programs get compiled to portable Python 3 code. DistAlgo was developed at the `Department of Computer Science <http://www.cs.sunysb.edu/>`_ in Stony Brook University. It is used in the instruction of some graduate-level such as `CSE 535 Asynchronous Systems <http://www.cs.stonybrook.edu/~liu/cse535/>`_ by `Annie Liu <http://www.cs.sunysb.edu/~liu/>`_ and `CSE 594 Distributed Systems <http://www.cs.sunysb.edu/~stoller/cse594/>`_ by `Scott Stoller <http://www.cs.sunysb.edu/~stoller/>`_.

### The Distributed Graph Algorithms
The following distributed graph algorithms that have implemented using **DistAlgo-0.2**:

1. `Minimum Spanning Tree`_ (https://github.com/arjungmenon/Distributed-Graph-Algorithms/tree/master/Minimum-Spanning-Tree)
2. `Maximal Independent Set`_ (https://github.com/arjungmenon/Distributed-Graph-Algorithms/tree/master/Maximal-Independent-Set)
3. `Breadth First Search`_ (https://github.com/arjungmenon/Distributed-Graph-Algorithms/tree/master/Breadth-First-Search)
4. `Shortest Path`_ (https://github.com/arjungmenon/Distributed-Graph-Algorithms/tree/master/ShortestPath)

.. _Minimum Spanning Tree: https://github.com/arjungmenon/Distributed-Graph-Algorithms/tree/master/Minimum-Spanning-Tree
.. _Maximal Independent Set: https://github.com/arjungmenon/Distributed-Graph-Algorithms/tree/master/Maximal-Independent-Set
.. _Breadth First Search: https://github.com/arjungmenon/Distributed-Graph-Algorithms/tree/master/Breadth-First-Search
.. _Shortest Path: https://github.com/arjungmenon/Distributed-Graph-Algorithms/tree/master/ShortestPath)

The subdirectory of each algorithm contains a relevant ***ReadMe*** file that describes the algorithm in detail with specific information about its implementation, limitations, etc.

#### Code Length
Lines of Code have never really been a good statistic on how long it took to write a piece of code. In addition, certain languages are more dense than others. For example this single statement turns a graph file into a list of NetworkX edges: ``( edge(ed.split()[0], ed.split()[1], int(ed.split()[2])) for ed in (e.strip() for e in f.readlines() if e.strip() != "") if len(ed.split()) == 3 )``. It would however taken a lot more code in an arcance language like Java. Andrew Tanenbaum mentions in one his awesome books (quoting Fred Brooke's mythical man-moth I believe) how IBM measured the performance of their programmers based on how many lines of code they wrote -- in assembly. Needless to say, the project (System/360) wasn't very successful.

However, I still think the *lines of code* would be an interesting statistic, so I'm providing it below:

+----------------------+------------+-----------+
| File name            | sloc only  | all lines |
+======================+============+===========+
| MST.dis.py           |    319     |    421    |
+----------------------+------------+-----------+
| tools.py             |    67      |    95     |
+----------------------+------------+-----------+
| MIS.dis.py           |    158     |    212    |
+----------------------+------------+-----------+
| BFS.dis              |    110     |    147    |
+----------------------+------------+-----------+
| ShortestPath.dis.py  |    43      |    60     |
+----------------------+------------+-----------+
| InputGraph.dis.py    |    36      |    50     |
+----------------------+------------+-----------+
| TOTAL   (proper)     |    733     |    985    |
+----------------------+------------+-----------+
| Kruskal.py           |    69      |    93     |
+----------------------+------------+-----------+
| mst_attempt_1.dis    |    204     |    276    |
+----------------------+------------+-----------+
| mst_attempt_1.dis    |    186     |    247    |
+----------------------+------------+-----------+
| TOTAL  (incl other)  |    1192    |    1601   |
+----------------------+------------+-----------+

Notes on the line count

- Other files such as ``run.py`` and ``sequential_messaging_test.dis`` that were not directly relevant to project have not been listed above.
- ``tools.py`` is used by MST for non-core functionalities. Two slightly different versions of ``InputGraph.py`` is used by BFS and Shortest Path to process the graph; the count is for the longer one.

#### Note about References
All references have been hyperlinked in-place using [Markdown's link syntax](http://daringfireball.net/projects/markdown/syntax#link).

### Other
[Ricart-Agrawala's and Suzuki-Kasami's token-based distributed mutex algorithms](https://github.com/arjungmenon/Distributed-Graph-Algorithms/tree/master/DistributedMutex) have also been been implemented in DistAlgo-0.2. In addition, [Lamport's fast mutual exclusion and bakery algorithms](https://github.com/arjungmenon/Distributed-Graph-Algorithms/tree/master/ConcurrentMutex) have been implemented using the built-in Python library ``threading``.
