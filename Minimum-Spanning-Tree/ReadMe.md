Distributed Minimum Spanning Tree
=================================
This is a distributed program that implements a distributed [Minimum Spanning Tree](https://en.wikipedia.org/wiki/Minimum_spanning_tree) solver in DistAlgo.

The algorithm used here to solve for the distributed MST problem is the classic canonical one by R. G. Gallager, P. A. Humblet and P. M. Spira. This algorithm, commonly known as GHS, is the best known algorithm (_state of art_) for the problem. I've added following documents to this repository which describe the GHS algorithm in detail:
* The [Original paper by Gallager, Humblet and Spira](https://raw.github.com/arjungmenon/DistAlgo/master/Minimum-Spanning-Tree/ghs.pdf) from 1983.
* A better paper (much nicer looking) based on the original prepared by [Guy Flysher and Amir Rubinshtein](https://raw.github.com/arjungmenon/DistAlgo/master/Minimum-Spanning-Tree/MST.pdf). (**recommended**)

The following diagram (from Guy Flysher and Amir Rubinshtein's version of the GHS paper) depicts the core idea behing the algorithm:
![Distributed MST by Gallager, Humblet & Spira](https://raw.github.com/arjungmenon/DistAlgo/master/Minimum-Spanning-Tree/MST-figure.png)

The following is pseudocode for the GHS algorithm (taken from Guy Flysher and Amir Rubinshtein's version of the GHS paper):
![Distributed MST by Gallager, Humblet & Spira](https://raw.github.com/arjungmenon/DistAlgo/master/Minimum-Spanning-Tree/MST_algorithm.png)
