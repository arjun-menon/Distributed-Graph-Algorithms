Distributed Minimum Spanning Tree
=================================

Introduction
------------
This is a distributed program that implements a distributed [Minimum Spanning Tree](https://en.wikipedia.org/wiki/Minimum_spanning_tree) solver in DistAlgo.

The algorithm used here to solve for the distributed MST problem is the classic canonical one by R. G. Gallager, P. A. Humblet and P. M. Spira. This algorithm, commonly known as GHS, is the best known algorithm (***state of art***) for the problem. I've added following documents to this repository which describe the GHS algorithm in detail:
* The [Original paper by Gallager, Humblet and Spira](https://raw.github.com/arjungmenon/DistAlgo/master/Minimum-Spanning-Tree/papers/GHS_original.pdf) from 1983.
* A much better looking paper based on the original, [prepared by Guy Flysher and Amir Rubinshtein](https://raw.github.com/arjungmenon/DistAlgo/master/Minimum-Spanning-Tree/papers/GHS_enhanced.pdf). (*recommended*)

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
