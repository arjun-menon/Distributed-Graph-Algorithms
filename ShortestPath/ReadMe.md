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
4. As this process occurs, every node receives one or more messages with the weight of a path to it _from the source node_.
5. The `newWeight` function when being invoked on the target node, prints out the weight and path to it indicated by the message received.
6. For simplicity, the termination/base case was omitted. The algorithm prints out multiple output messages as new paths are received. The last path printed _is the shortest path_ from the source node to the target nodee. To terminate, the algorithm would have to involve additional stuff such as each node sending back replies to the messages sent by the `propogate` function, as well as keeping track of the number of replies received and waiting for the total replies received to equal messages sent at each node.


