Distributed Minimum Spanning Tree
=================================

Introduction
------------
This is a distributed program that implements a distributed [Minimum Spanning Tree](https://en.wikipedia.org/wiki/Minimum_spanning_tree) solver in DistAlgo.


### Problem Description

A spanning tree is defined as a tree which is a sub-graph of a given graph and connects all the nodes in the graph. The graph must be a _connected_ and _undirected_ graph. A [Minimum Spanning Tree](https://en.wikipedia.org/wiki/Minimum_spanning_tree) is a spanning tree whose sum of weights of the edges is the lowest of all possible spanning trees for the given graph.

#### Same graph, multiple minimum spanning trees

If a graph has multiple edges *with the same weight*, then the graph could have several MSTs. This situation can be obviated by constructing a grpah whose edges have unique weights.

### Algroithms

#### Sequential Solvers

There are two commonly used for finding the MST of a graph **sequentially**: *Prim's algorithm* and *Kruskal's algorithm*. To better understand the problem and get a feel for it, I wrote a Kruskal's solver which can found at `Kruskal.py`.

#### Distributed Solvers

The problem here is radically different from the previous one -- here the nodes of the graph are nodes in a distributed system; i.e. a set of computers/processes where each computer represents a node of the graph and the edge between two nodes of the graph respresent a _valid communication interlink_ between two computers.

The best known algorithm that solves this problem is the GHS algorithm of R. G. Gallager, P. A. Humblet and P. M. Spira. [According to Wikipedia](https://en.wikipedia.org/wiki/Distributed_minimum_spanning_tree), there also is a parallelization of Prim's sequential algorithm by Nobri et al. Teh GHS algorithm could be thought of as the **state of art** for distributed MST. I have implemented the GHS algorithm using DistAlgo, a seuperset of Python enhanced for distributed programming by Annie Liu, Bo Lin et al. from Stony Brook University.

I found two papers online that describe GHS. One is the original from 1983, by Gallager, Humlbet & Spira. The other is an enhanced version of the original (with better graphics, typesetting, explanation, etc.) prepared by Guy Flysher and Amir Rubinshtein. I followed the second one while creating my implementation in DistAlgo.

I've posted PDFs of both papers (found online) in this GitHub repo under the `papers` directory. Links to them are below:

* The [Original paper by Gallager, Humblet and Spira](https://raw.github.com/arjungmenon/DistAlgo/master/Minimum-Spanning-Tree/papers/GHS_original.pdf) from 1983.
* The one [prepared by Guy Flysher and Amir Rubinshtein](https://raw.github.com/arjungmenon/DistAlgo/master/Minimum-Spanning-Tree/papers/GHS_enhanced.pdf). (*I recommend this one*)

Implementation
--------------

### Usage

Both the distributed `MST.dis` and the sequential `Kruskal.py` share a common 
set of tools encapsulated in the module `tools.py`. `tools.py` handles all the 
arguments supplied by the user. It builds from the *graph file*, the NetworkX 
graph object used by the solvers. The graph file lists all the edges in 
the graph in [CSV](https://en.wikipedia.org/wiki/Comma-separated_values)-style, 
except without the commas. By default `graph-2` is used.

The available arguments and their uses can be displayed by passing the `-h` argument:

	usage: MST.dis [-h] [-v] [-b BACKEND] [graph]

	Finds the Minimum Spanning Tree (MST) of a given graph.

	positional arguments:
	  graph                 File listing the edges of a graph line-by-line in the
	                        following style: "A B 2", where "A" and "B" are node
	                        names and "2" is the weight of the edge connecting
	                        them.

	optional arguments:
	  -h, --help            show this help message and exit
	  -v, --visualize       Visualize the graph and its solution using matplotlib,
	                        with the branches of the MST marked in thick blue.
	  -b BACKEND, --backend BACKEND
	                        Interactive GUI backend to be used by matplotlib for
	                        visualization. Potential options are: GTK, GTKAgg,
	                        GTKCairo, FltkAgg, MacOSX, QtAgg, Qt4Agg, TkAgg, WX,
	                        WXAgg, CocoaAgg, GTK3Cairo, GTK3Agg. Default value is
	                        Qt4Agg.

Core Ideas
----------
The following diagram (from Guy Flysher and Amir Rubinshtein's version of the GHS paper) depicts the core idea behing the algorithm:

![Diagram showing fragment mergers and absorptions](https://raw.github.com/arjungmenon/DistAlgo/master/Minimum-Spanning-Tree/img/MST-figure.png)

Pseudocode from the paper
-------------------------
The following is pseudocode for the GHS algorithm (taken from Guy Flysher and Amir Rubinshtein's version of the GHS paper):

![Distributed MST by Gallager, Humblet & Spira](https://raw.github.com/arjungmenon/DistAlgo/master/Minimum-Spanning-Tree/img/MST_algorithm.png)

Test Cases
----------
This diagram depicts one of the test cases used to tes the algorithm:

![Test Case 1](https://raw.github.com/arjungmenon/DistAlgo/master/Minimum-Spanning-Tree/img/test_case_1.png)

The think blue edges denote the branches of the MST (Minimum Spanning Tree).
