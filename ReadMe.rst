Distributed Graph Algorithms in DistAlgo
========================================

This repository contains the implementations of some *distributed* graph algorithms as well as two token-based mutex algorithms in *DistAlgo*. DistAlgo is a superset of Python that adds special constructs to Python for specifying distributed algorithms in a high-level and succint manner. DistAlgo programs get compiled to portable Python 3 code. DistAlgo was developed at the `Department of Computer Science <http://www.cs.sunysb.edu/>`_ in Stony Brook University. It is used in the instruction of some graduate courses such as `CSE 535 Asynchronous Systems <http://www.cs.stonybrook.edu/~liu/cse535/>`_ by `Annie Liu <http://www.cs.sunysb.edu/~liu/>`_ and `CSE 594 Distributed Systems <http://www.cs.sunysb.edu/~stoller/cse594/>`_ by `Scott Stoller <http://www.cs.sunysb.edu/~stoller/>`_.

The Distributed Graph Algorithms
--------------------------------
The following distributed graph algorithms that have implemented using **DistAlgo-0.2**:

1. `Minimum Spanning Tree`_
2. `Maximal Independent Set`_
3. `Breadth First Search`_
4. `Shortest Path`_

.. _Minimum Spanning Tree: https://github.com/arjungmenon/Distributed-Graph-Algorithms/tree/master/Minimum-Spanning-Tree
.. _Maximal Independent Set: https://github.com/arjungmenon/Distributed-Graph-Algorithms/tree/master/Maximal-Independent-Set
.. _Breadth First Search: https://github.com/arjungmenon/Distributed-Graph-Algorithms/tree/master/Breadth-First-Search
.. _Shortest Path: https://github.com/arjungmenon/Distributed-Graph-Algorithms/tree/master/ShortestPath

The subdirectory of each algorithm contains a relevant **ReadMe** file that describes the algorithm in detail with specific information about its implementation, limitations, etc. The ReadMe should be viewed in GitHub or with a Markdown converter as it contains images, styling, sections, etc.

Note about References
~~~~~~~~~~~~~~~~~~~~~
All references have been hyperlinked **in-place** using `Markdown's link syntax <http://daringfireball.net/projects/markdown/syntax#link>`_.

NetworkX
~~~~~~~~
A graph library known as `NetworkX <http://networkx.lanl.gov/>`_ was used in this project. It is a well-renown pure Python library that provides several useful features pertaining to graphs. Granted, it was a bit unnecessary for this project, but I was anticipating more use for it than was needed.

Code Length
-----------
Lines of Code have never really been a good statistic on how long it took to write a piece of code. In addition, certain languages are more dense than others. For example this segment of Python code extracts lines from a graph file under certain constraints: ``... for ed in (e.strip() for e in f.readlines() if e.strip() != "") if len(ed.split()) == 3``. It probably would however have taken several lines of code if written in Java. Also, `Andrew Tanenbaum <http://en.wikipedia.org/wiki/Andrew_S._Tanenbaum>`_ mentions in one his awesome books (quoting `Fred Brooke <http://en.wikipedia.org/wiki/Fred_Brooks>`_'s `mythical man-moth <http://en.wikipedia.org/wiki/The_Mythical_Man-Month>`_ I believe) how IBM measured the performance of their programmers based on how many lines of code they wrote -- in assembly. Needless to say, the project (`OS/360 <http://en.wikipedia.org/wiki/OS/360>`_) wasn't very successful.

However, I still think the *lines of code* would be an interesting statistic, so here it is:

+----------------------+------------+-----------+
| File name            | sloc only  | all lines |
+======================+============+===========+
| MST.dis.py           |    319     |    421    |
+----------------------+------------+-----------+
| MIS.dis.py           |    158     |    212    |
+----------------------+------------+-----------+
| BFS.dis.py           |    119     |    154    |
+----------------------+------------+-----------+
| ShortestPath.dis.py  |    43      |    60     |
+----------------------+------------+-----------+
| InputGraph.dis.py    |    36      |    50     |
+----------------------+------------+-----------+
| tools.py             |    67      |    95     |
+----------------------+------------+-----------+
| TOTAL   (proper)     |    742     |    992    |
+----------------------+------------+-----------+
| Kruskal.py           |    69      |    93     |
+----------------------+------------+-----------+
| mst_attempt_1.dis    |    204     |    276    |
+----------------------+------------+-----------+
| mst_attempt_1.dis    |    186     |    247    |
+----------------------+------------+-----------+
| TOTAL  (incl other)  |    1201    |    1608   |
+----------------------+------------+-----------+

Notes on the line count
~~~~~~~~~~~~~~~~~~~~~~~

- Other files such as ``run.py`` and ``sequential_messaging_test.dis``, that were not directly relevant to project have not been listed above.
- **TOTAL (proper)** is the line count for all the active project code. ``Kruskal.py`` and ``mst_attempt_*`` were experimental files written while developing MST and are no longer used.
- Two slightly different versions of ``InputGraph.py`` is used by BFS and Shortest Path to process the graph; the count is for the longer one.
- ``tools.py`` is used by MST for non-core functionalities (like building the graph, visualizing, etc.)

Other
-----
`Ricart-Agrawala's and Suzuki-Kasami's token-based distributed mutex algorithms <https://github.com/arjungmenon/Distributed-Graph-Algorithms/tree/master/DistributedMutex>`_ have also been been implemented in DistAlgo-0.2. In addition, `Lamport's fast mutual exclusion and bakery algorithms <https://github.com/arjungmenon/Distributed-Graph-Algorithms/tree/master/ConcurrentMutex>`_ have been implemented using the built-in Python library ``threading``.