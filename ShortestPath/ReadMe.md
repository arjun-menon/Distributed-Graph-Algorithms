Shortest Path
-------------

#### Problem Description

The [shortest path problem](https://en.wikipedia.org/wiki/Shortest_path_problem) as we all know is the quest to find the shortest path between two nodes in a connected weighted undirected graph.

### Algorithm

The problem was pretty straighforward and simple, so I didn't see a need to research it online. So I designed my own algorithm for it. The algorithm is described in the next section.

#### Steps involved in the algorithm

1. The inital node, or _source_ node calls a function `newWeight`.
2. `newWeight` sets the "total weight" of the path to _itself_ as 0.
3. It then calls a function `propogate` which sends every neighboring the weight of the path leading from the source to _that node_ as: the sum of the weight to the current node + the weight of the edge between the current node and the neighboring node.
4. As this process occurs, every node receives one or more messages with the weight of a path to it _from the source node_. If the new weight it received is less than its previous weight (all nodes start at `999999` or infinite weight), it replaces that lower weight with its current weight _and_ contintues the `proprogate` / propogation process.
5. The `newWeight` function when being invoked on the target node, prints out the weight and path to it indicated by the message received.
6. For simplicity, the termination/base case was omitted. The algorithm prints out multiple output messages as new paths are received. The last path printed _is the shortest path_ from the source node to the target nodee. To terminate, the algorithm would have to involve additional stuff such as each node sending back replies to the messages sent by the `propogate` function, as well as keeping track of the number of replies received and waiting for the total replies received to equal messages sent at each node.


Testing
-------

### Graph 1

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

	[2012-10-14 03:07:20,411]runtime:INFO: Creating instances of P..
	[2012-10-14 03:07:20,424]runtime:INFO: 10 instances of P created.
	[2012-10-14 03:07:20,434]runtime:INFO: Starting procs...
	[2012-10-14 03:07:20,438]P(C):INFO: New shortest path of weight 34: G -> E -> I -> C
	[2012-10-14 03:07:20,439]P(C):INFO: New shortest path of weight 25: G -> E -> D -> C
	[2012-10-14 03:07:22,138]runtime:INFO: Received keyboard interrupt.
	[2012-10-14 03:07:22,138]runtime:INFO: ***** Statistics *****
	* Total procs: 10

#### Run 3 (G to C)

	[2012-10-14 03:42:20,441]runtime:INFO: Creating instances of P..
	[2012-10-14 03:42:20,455]runtime:INFO: 10 instances of P created.
	[2012-10-14 03:42:20,465]runtime:INFO: Starting procs...
	[2012-10-14 03:42:20,474]P(C):INFO: New shortest path of weight 45: G -> H -> I -> C
	[2012-10-14 03:42:20,476]P(C):INFO: New shortest path of weight 29: G -> F -> A -> B -> C
	[2012-10-14 03:42:20,480]P(C):INFO: New shortest path of weight 25: G -> E -> D -> C
	[2012-10-14 03:42:22,243]runtime:INFO: Received keyboard interrupt.
	[2012-10-14 03:42:22,244]runtime:INFO: ***** Statistics *****
	* Total procs: 10

### Graph 2

#### Run 1 (G to C)

	[2012-10-14 03:59:18,615]runtime:INFO: Creating instances of P..
	[2012-10-14 03:59:18,632]runtime:INFO: 13 instances of P created.
	[2012-10-14 03:59:18,640]runtime:INFO: Starting procs...
	[2012-10-14 03:59:18,644]P(C):INFO: New shortest path of weight 45: G -> H -> I -> C
	[2012-10-14 03:59:18,650]P(C):INFO: New shortest path of weight 34: G -> E -> I -> C
	[2012-10-14 03:59:18,651]P(C):INFO: New shortest path of weight 29: G -> F -> A -> B -> C
	[2012-10-14 03:59:18,652]P(C):INFO: New shortest path of weight 25: G -> E -> D -> C
	[2012-10-14 03:59:24,011]runtime:INFO: Received keyboard interrupt.
	[2012-10-14 03:59:24,012]runtime:INFO: ***** Statistics *****
	* Total procs: 13

#### Run 2 (G to C)

	[2012-10-14 04:21:59,424]runtime:INFO: Creating instances of P..
	[2012-10-14 04:21:59,442]runtime:INFO: 13 instances of P created.
	[2012-10-14 04:21:59,449]runtime:INFO: Starting procs...
	[2012-10-14 04:21:59,454]P(C):INFO: New shortest path of weight 29: G -> F -> A -> B -> C
	[2012-10-14 04:21:59,459]P(C):INFO: New shortest path of weight 25: G -> E -> D -> C
	[2012-10-14 04:22:02,182]runtime:INFO: Received keyboard interrupt.
	[2012-10-14 04:22:02,182]runtime:INFO: ***** Statistics *****
	* Total procs: 13

#### Run 3 (G to L)

	[2012-10-14 04:30:48,914]runtime:INFO: Creating instances of P..
	[2012-10-14 04:30:48,932]runtime:INFO: 13 instances of P created.
	[2012-10-14 04:30:48,936]runtime:INFO: Starting procs...
	[2012-10-14 04:30:48,943]P(L):INFO: New shortest path of weight 72: G -> H -> J -> K -> L
	[2012-10-14 04:30:48,944]P(L):INFO: New shortest path of weight 68: G -> E -> H -> J -> K -> L
	[2012-10-14 04:30:54,303]runtime:INFO: Received keyboard interrupt.
	[2012-10-14 04:30:54,304]runtime:INFO: ***** Statistics *****
	* Total procs: 13
