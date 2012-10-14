Shortest Path
=============

The [shortest path problem](https://en.wikipedia.org/wiki/Shortest_path_problem) as we all know is the quest to find the shortest path between two nodes in a connected weighted undirected graph.

Algorithm
---------

The problem was pretty straighforward and simple, so I didn't see a need to research it online. I designed my own algorithm for it. My algorithm is described in the next section.

### Steps involved in the algorithm

1. The inital node, or _source_ node calls a function `newWeight`.
2. `newWeight` sets the "total weight" of the path to _itself_ as 0.
3. It then calls a function `propogate` which sends every neighboring the weight of the path leading from the source to _that node_ as: the sum of the weight to the current node + the weight of the edge between the current node and the neighboring node.
4. As this process occurs, every node receives one or more messages with the weight of a path to it _from the source node_. If the new weight it received is less than its previous weight (all nodes start at `999999` or infinite weight), it replaces that lower weight with its current weight _and_ contintues the `proprogate` / propogation process.
5. The `newWeight` function when being invoked on the target node, prints out the weight and path to it indicated by the message received.
6. For simplicity, the termination/base case was omitted. The algorithm prints out multiple output messages as new paths are received. The last path printed _is the shortest path_ from the source node to the target nodee. To terminate, the algorithm would have to involve additional stuff such as each node sending back replies to the messages sent by the `propogate` function, as well as keeping track of the number of replies received and waiting for the total replies received to equal messages sent at each node.

Usage
-----

The program can be run easily from the terminal by typing `python3 -m distalgo.runtime ShortestPath.dis` or by executing `run.py`.

`ShortestPath.dis` offers several command-line options. These can be listed by passing in the `-h` argument:

	usage: ShortestPath.dis [-h] [-s SOURCE] [-t TARGET] [graph]

	Finds the shortest path.

	positional arguments:
	  graph                 File listing the edges of a graph line-by-line in the
	                        following style: "A B 2", where "A" and "B" are node
	                        names and "2" is the weight of the edge connecting
	                        them.

	optional arguments:
	  -h, --help            show this help message and exit
	  -s SOURCE, --source SOURCE
	                        The source node.
	  -t TARGET, --target TARGET
	                        The target node.

The first of these is `graph` which is an input graph. It defaults to `graph-1`. The other two are the **source** and **target** nodes between which to find the shortest path.

Testing
-------

In each run, differences can be seen in the "shortest" paths found priot to the actual and final shortest paths. This factor is random/non-deterministic.

### Graph 1

I used the `graph-1` from MST to test Shortest Path. This is a diagram of that graph, generated using _NetworkX_ and _matplotlib_:

![Test Case 1](https://raw.github.com/arjungmenon/Distributed-Graph-Algorithms/master/Maximal-Independent-Set/graph-1.png)

 The following runs are all for the shortest path from `G` to `C`:

#### Run 1 (G to C)

	[2012-10-14 03:07:17,334]runtime:INFO: Creating instances of P..
	[2012-10-14 03:07:17,363]runtime:INFO: 10 instances of P created.
	[2012-10-14 03:07:17,369]runtime:INFO: Starting procs...
	[2012-10-14 03:07:17,374]P(C):INFO: New shortest path of weight 45: G -> H -> I -> C
	[2012-10-14 03:07:17,376]P(C):INFO: New shortest path of weight 25: G -> E -> D -> C
	[2012-10-14 03:07:19,245]runtime:INFO: Received keyboard interrupt.
	[2012-10-14 03:07:19,246]runtime:INFO: ***** Statistics *****
	* Total procs: 10

#### Run 2 (G to C)

	[2012-10-14 03:42:20,441]runtime:INFO: Creating instances of P..
	[2012-10-14 03:42:20,455]runtime:INFO: 10 instances of P created.
	[2012-10-14 03:42:20,465]runtime:INFO: Starting procs...
	[2012-10-14 03:42:20,474]P(C):INFO: New shortest path of weight 45: G -> H -> I -> C
	[2012-10-14 03:42:20,476]P(C):INFO: New shortest path of weight 29: G -> F -> A -> B -> C
	[2012-10-14 03:42:20,480]P(C):INFO: New shortest path of weight 25: G -> E -> D -> C
	[2012-10-14 03:42:22,243]runtime:INFO: Received keyboard interrupt.
	[2012-10-14 03:42:22,244]runtime:INFO: ***** Statistics *****
	* Total procs: 10

#### Run 3 (G to C)

	[2012-10-14 03:59:18,615]runtime:INFO: Creating instances of P..
	[2012-10-14 03:59:18,632]runtime:INFO: 10 instances of P created.
	[2012-10-14 03:59:18,640]runtime:INFO: Starting procs...
	[2012-10-14 03:59:18,644]P(C):INFO: New shortest path of weight 45: G -> H -> I -> C
	[2012-10-14 03:59:18,650]P(C):INFO: New shortest path of weight 34: G -> E -> I -> C
	[2012-10-14 03:59:18,651]P(C):INFO: New shortest path of weight 29: G -> F -> A -> B -> C
	[2012-10-14 03:59:18,652]P(C):INFO: New shortest path of weight 25: G -> E -> D -> C
	[2012-10-14 03:59:24,011]runtime:INFO: Received keyboard interrupt.
	[2012-10-14 03:59:24,012]runtime:INFO: ***** Statistics *****
	* Total procs: 10

### Graph 2

Here I used `graph-2` which has also been used to test both MST and MIS. Here is a diagram of that graph, generated using _NetworkX_ and _matplotlib_:

![Test Case 2](https://raw.github.com/arjungmenon/Distributed-Graph-Algorithms/master/Maximal-Independent-Set/graph-2b.png)

Here multiple runs have been made with non-default different start and end nodes.

#### Run 1 (G to L)

	[2012-10-14 04:30:48,914]runtime:INFO: Creating instances of P..
	[2012-10-14 04:30:48,932]runtime:INFO: 13 instances of P created.
	[2012-10-14 04:30:48,936]runtime:INFO: Starting procs...
	[2012-10-14 04:30:48,943]P(L):INFO: New shortest path of weight 72: G -> H -> J -> K -> L
	[2012-10-14 04:30:48,944]P(L):INFO: New shortest path of weight 68: G -> E -> H -> J -> K -> L
	[2012-10-14 04:30:54,303]runtime:INFO: Received keyboard interrupt.
	[2012-10-14 04:30:54,304]runtime:INFO: ***** Statistics *****
	* Total procs: 13

#### Run 2 (A to M)

	[2012-10-14 05:10:16,912]runtime:INFO: Creating instances of P..
	[2012-10-14 05:10:16,929]runtime:INFO: 13 instances of P created.
	[2012-10-14 05:10:16,940]runtime:INFO: Starting procs...
	[2012-10-14 05:10:16,954]P(M):INFO: New shortest path of weight 82: A -> F -> G -> H -> J -> K -> M
	[2012-10-14 05:10:16,957]P(M):INFO: New shortest path of weight 66: A -> F -> E -> H -> J -> K -> M
	[2012-10-14 05:10:17,833]runtime:INFO: Received keyboard interrupt.
	[2012-10-14 05:10:17,834]runtime:INFO: ***** Statistics *****
	* Total procs: 13

#### Run 3 (A to M)

	[2012-10-14 05:10:18,816]runtime:INFO: Creating instances of P..
	[2012-10-14 05:10:18,833]runtime:INFO: 13 instances of P created.
	[2012-10-14 05:10:18,842]runtime:INFO: Starting procs...
	[2012-10-14 05:10:18,855]P(M):INFO: New shortest path of weight 92: A -> B -> C -> I -> J -> K -> M
	[2012-10-14 05:10:18,858]P(M):INFO: New shortest path of weight 86: A -> B -> C -> D -> I -> J -> K -> M
	[2012-10-14 05:10:18,860]P(M):INFO: New shortest path of weight 77: A -> B -> D -> I -> J -> K -> M
	[2012-10-14 05:10:18,861]P(M):INFO: New shortest path of weight 72: A -> F -> E -> D -> I -> J -> K -> M
	[2012-10-14 05:10:18,862]P(M):INFO: New shortest path of weight 67: A -> F -> E -> I -> J -> K -> M
	[2012-10-14 05:10:18,863]P(M):INFO: New shortest path of weight 66: A -> F -> E -> H -> J -> K -> M
	[2012-10-14 05:10:20,452]runtime:INFO: Received keyboard interrupt.
	[2012-10-14 05:10:20,453]runtime:INFO: ***** Statistics *****
	* Total procs: 13

#### Run 4 (B to K)

	[2012-10-14 12:21:21,161]runtime:INFO: Creating instances of P..
	[2012-10-14 12:21:21,179]runtime:INFO: 13 instances of P created.
	[2012-10-14 12:21:21,187]runtime:INFO: Starting procs...
	[2012-10-14 12:21:21,200]P(K):INFO: New shortest path of weight 67: B -> C -> I -> J -> K
	[2012-10-14 12:21:21,201]P(K):INFO: New shortest path of weight 63: B -> A -> F -> G -> H -> J -> K
	[2012-10-14 12:21:21,202]P(K):INFO: New shortest path of weight 59: B -> A -> F -> G -> E -> H -> J -> K
	[2012-10-14 12:21:21,203]P(K):INFO: New shortest path of weight 47: B -> A -> F -> E -> H -> J -> K
	^C[2012-10-14 12:21:23,943]runtime:INFO: Received keyboard interrupt.
	[2012-10-14 12:21:23,944]runtime:INFO: ***** Statistics *****
	* Total procs: 13

---