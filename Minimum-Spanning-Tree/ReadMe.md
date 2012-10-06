Distributed Minimum Spanning Tree
=================================

Introduction
------------
This is a distributed program that implements a distributed [Minimum Spanning Tree](https://en.wikipedia.org/wiki/Minimum_spanning_tree) solver in DistAlgo.

The algorithm used here to solve for the distributed MST problem is the classic canonical one by R. G. Gallager, P. A. Humblet and P. M. Spira. This 
algorithm, commonly known as GHS, is the best known algorithm (***state of art***) for the problem. 
I've added following documents to this repository which describe the GHS algorithm in detail:
* The [Original paper by Gallager, Humblet and Spira](https://raw.github.com/arjungmenon/DistAlgo/master/Minimum-Spanning-Tree/papers/GHS_original.pdf) from 1983.
* A much better looking paper based on the original, [prepared by Guy Flysher and Amir Rubinshtein](https://raw.github.com/arjungmenon/DistAlgo/master/Minimum-Spanning-Tree/papers/GHS_enhanced.pdf). (*recommended*)

Usage
-----
Both the distributed `MST.dis` and sequential `Kruskal.py` share a common 
set of tools encapsulated in the module `tools.py`. Tools handles the 
_optargs_ supplied by the user. It builds from the *graph file*, the NetworkX 
graph object used by the solvers. The graph file lists all the edges in 
the graph in [CSV](https://en.wikipedia.org/wiki/Comma-separated_values)-style, 
except without the commas.

The optargs and their purposes can be displayed by passing the '-h' argument:

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

The blue edges denote the branches of the MST (Minimum Spanning Tree).
