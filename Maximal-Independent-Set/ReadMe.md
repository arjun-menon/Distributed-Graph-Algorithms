Distributed Maximal Independent Set
===================================

Overview
--------

### Problem Description

This algorithms solves the [Maximal independent set](https://en.wikipedia.org/wiki/Maximal_independent_set "Wikipedia") problem in a distributed system where the nodes are represented by processes and edges between the nodes in the graph represent a valid communication link between these processes. The maximal independent set problem is described in detail in its [Wikipedia article](https://en.wikipedia.org/wiki/Maximal_independent_set). One of its many applications is [graph coloring](https://en.wikipedia.org/wiki/Graph_coloring).

#### Multiple Maximal Independent Sets for the same graph

For one graph, there can be more than one, and often several maximal independent sets. Most algorithms that solve for maximal independent set *involve some* ***random*** *factor*, so we can expect different solutions to the MIS problem in different runs of the algorithm.

The following diagram [from Wikipedia](http://en.wikipedia.org/w/index.php?title=File:Cube-maximal-independence.svg) for the graph of a cube shows the 6 different possible MISs for it:

![MISs for Cube](https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Cube-maximal-independence.svg/500px-Cube-maximal-independence.svg.png)

#### Related NP-complete problems

There is another problem -- one that tries to find enumerate _all possible MISs_ for a given graph. This problem is much more harder to solve, and is known to be NP-complete. Another similar sounding but different problem is _Maxim***um*** independent set_ which tries to find the largest MIS possible. It does so by using the NP-complete MIS enumeration/listing algorithm, then picking the largest MIS it returns. Obviously it is NP-complete too. Here I solve for the _Maxim***al*** independent set_ problem.

### Best Algorithms

A quick [Google search](https://www.google.com/search?q=parallel+maximal+independent+set) for "distributed maximal independent set" reveals a few algorithms for solving for Maximal Independent Set. The top among these is [A Log-Star Distributed Maximal Independent Set Algorithm](http://disco.ethz.ch/publications/podc08SW.pdf) by Johannes Schneider, Roger Wattenhofer. Another major one that comes up when searching for "parallel maximal independent srt" instead is Luby's algorithm ([the original paper](http://www.dcg.ethz.ch/alumni/pascal/refs/mis_1986_luby.pdf) and [lecture notes on it](http://www.cc.gatech.edu/~vigoda/RandAlgs/MIS.pdf)).

However after looking at these algorithms for a while, I decided to instead design my own solution to the distributed Maximal Independent Set problem. Luby's algorithm for instance, seemed a little more complicated than necessary to me. The complication was probably an optimization for performance. It involves (based on my understanding) picking a random set of vertices, breaking "ties" in the set -- i.e. vertices that formed edges in the random set, and doing something else and repeating the process. In addition, the lecture notes and paper on Luby's algorith, weren't very clear on how the interprocess communication was to be modeled. (In contrast, the GHS paper for MST was very clear about this.) However, it was pretty clear to me what the straightforward parallelization (distribution) of the sequential MIS algorithm would look like, so I decided to design my own distributed algorithm based on it.

Description of the Algorithm
----------------------------
### Design

The design of my algorithm largely follows the fundamental idea underpinning the sequential algorithm. The sequential algorithm (taken from these [Luby's algorithm lecture notes](http://www.cc.gatech.edu/~vigoda/RandAlgs/MIS.pdf)) for finding MST is shown below:

![MIS Sequential](https://raw.github.com/arjungmenon/Distributed-Graph-Algorithms/master/Maximal-Independent-Set/MIS-sequential.png)

The core steps in my algorithm are as follows:

* Initally all nodes are in a "normal" state. My algorithm, like Luby's involves a random factor. Initially, it picks a random node and marks it as a `VERTEX` of the MST.
* Next, this (randomly-picked) vertex marks _all its neighbors as_ `OUT`. This means they're not vertices.
* The randomly-picked vertex then performs a search for node in the graph, that is _neither a VERTEX nor OUT_ and when it finds, it marks that node as the next `VERTEX` and repeats the search-and-mark process again.
* It repeats this process until is able to find no more NORMAL nodes. At this point it knows the algorithm has ended, and it terminates the program.

### Conditions and Constraints
Some of the conditions and constraints placed placed on the algorithm and in the implementatin are:

 -  Each node in the graph is represented by a process.

 -  A process/node can only communicate with other processes/nodes 
    that it has an edge with. This constraint is soft-enforced.
    Although DistAlgo allows a process to communicate with any 
    other process, the algorithm does not communicate to any process 
    that it does not have an edge with. (An exception is the control 
    process, which is not key player in the algorithm.) This constraint 
    is crucial has been articially imposed upon this algorithm to imiate 
    real-life networks where there necessarily isn't a communication link 
    between every computer with every other computer.

 -  There's a special process known as the Control Process. The 
    Control Process fulfills three roles: (1) It iniates the algorithm.
    (2) It collects output. (3) It terminates the algorithm.

 -  The control process is not bound by constraint (a), and any process is 
    permitted to communicate to it and it to all other processes. However, 
    the control process isn't absolutely necessary to the algorithm, or a 
    crucial component of it. The initation of the algorithm could be moved to 
    top-level main() function, and rather than collect output, each node could 
    produce output declaring itself as a vertex of the MST (it does this already), 
    and termination could be handled by the last VERTEX node; albeit in a less
    elegant fashion. The control process is overall just a niceity that simplifies 
    and renders more elegant this particular implementation.

Usage
-----
The algorithm can be run by typing `python3 -m distalgo.runtime MIS.dis` or `run.py` at a POSIX terminal. The former relies on DistAlgo being installed as a library.

The following help message is generated when the `-h` option is passed:

    usage: MIS.dis [-h] [graph]

    Finds the vertices of the Maximal Independent Set (MST) of a given graph.

    positional arguments:
      graph       File listing the edges of a graph line-by-line in the following
                  style: "A B 2", where "A" and "B" are node names and "2" is the
                  weight of the edge connecting them.

    optional arguments:
      -h, --help  show this help message and exit

Thee only optarg is `graph` which is a graph file formatted in the manner specified in the help message. By default, if none is specified, `graph-1` is used.

Implementation Details
----------------------

### High-Level Overview

Each node/process can have one of 3 states: NORMAL, VERTEX, OUT.
Initally each node is NORMAL.

The algorithm follows the idea behind the sequential algorithm, and does the following:

 1. Picks a random node in the graph.
 2. Marks that node as a VERTEX, and the its neighbors as OUT.
 3. Looks for another node in the graph that is NORMAL (ie. not a VERTEX and not OUT)
 4. It repeats from step a, except instead of a random node, it's the node from step c.
 5. The base case, is when in step c, no NORMAL node could be found. When this happens, 
    the algorithm terminates.

Once crucial aspect is the search for the next NORMAL node. The random factor is present in this search too. The VERTEX initiating a search _randomly_ picks a neighboring node and asks it to search, and the process repeats recursively (with there being random selections at each repitition.) This (essential) random character helps us obtain **different** results for the program each time it is run.

### Properties of the functions mark(), OnSearch, search, OnSearchReply and the Control Process

This is an overview of some of the _key_ functions in the implementation.

Overview of **mark**():
* Marks a node as VERTEX,
* Sends messages to neighboring nodes telling them to mark themselves as OUT.
* Initiates a search for the next NORMAL node in the graph.
* If none could be found, informs the Control Process that the algorithm is finished.

Functions **OnSearch**(path), **search**(path, source), **OnSearchReply**(path):

 -  These functions together sweep through the graph in search for a NORMAL node.

 -  Initially, the search is kickstarted by mark(). `mark` directly 
    calls `search`. `search` then sends message to all its neighboring 
    nodes, asking them to participate in the search. `search`also waits 
    for replies from _all_ its neighboring nodes before doing anything 
    else. The `path` parameter of `search` allows it to keep a record of 
    the path to be taken to reach it from the marked node. This is used  
    later on by the marked node. The `search` function eventually, after the 
    completion of the search, returns a "path list": a list of paths leading 
    to all NORMAL nodes from the marked node.

 -  Each invocation of `search` is accompanied with a `path` from the initial 
    marked node to that particular node. At the beginning the `path` is `None`, 
    but for subsequent `search`es, the `path` paramter contains a list of nodes, 
    which lists the path to be taken to reach node X from the marked node.

 -  Each time a node is notified to join the search via the message `Search` 
    handled by `OnSearch`, the node checks if it is already pariticpating in a 
    search by that particular marked node (the one that iniated the search.)
    It does so by keeping a record of all the searches it has participated in, 
    in the set veriable `search_requested`. If a search request comes from a node 
    to "re-participate" in the search its already paritipating it, it effectively 
    rejects that request, by sending a reply consisting on an empty path list.

 -  Every time the `search` function realizes its own state is NORMAL, it adds 
    itself to variable `collected_replies` normally used to collect search replies 
    from other nodes. As the search progress and penetrates every last node in the 
    graph, atleast one node (usually more than one) will receive a reply from each of 
    its nodes, and all these replies will be empty lists. The reason for this could be 
    that all other nodes are already engaged in search, so rejected a second/third/etc 
    request for search from that particular node and/or that it is an VERTEX or OUT node.
    In either case the reply from all its niegbors initiates a domino effect, where this 
    node then replies to the node that invoked its search (which had been waiting for a 
    reply from this node), and that node to its "caller" node, and so on. The node that 
    replies first, will reply with a path list that contains only a path from the marked 
    node to itself. But the node that "called" it will receive this along with potentially 
    other non-empty path list. It will merge all these path lists into one, adding onto them 
    its own path in case it is a NORMAL node. This reverse cascade will continue until the 
    replies all merge into one, and is handed back to the original marked node.

More on **mark**() and the Control Process:

 -  The marked node, upon receiving the reply, picks a random path out of the path list, and 
    send it a message `Mark` with the `path` as parameter. This message (handled by `OnMark`) 
    will propogate itself until it reaches the node on the other of the path. Putting this in 
    Python's array/slice notation: `path[0] -> path[1] -> ... -> path[-1:]`
    The final recepient upon receiving the `Mark` will call the `mark()` function once more, 
    continue the process (of marking itself as a VERTEX, OUT-ing neighbors, searching) -- 
    until there are _no more NORMAL nodes left_. When this condition occurs, the marked node 
    will receive as a result to its `search`: an empty path list. At this point, this marked 
    node knows it is the last vertex of the MIS and that there are no more vertices in the MIS.
    Armed with this knowledge, it sends a `Finished` message to the control process, which promptly 
    flips the `done` boolean resulting in an automatic termination of all other processes.

 -  The control process also prints out a list of all the vertices 
    once more (although this could be inferred from the individual 
    output produced by each process as they got marked.) This is 
    accomplished by means of a `Marked` message sent by each process/node 
    when it gets marked as VERTEX or OUT. This feature accomplishes 
    purpose (2) of the control process: output collection.

Running & Testing
-----------------
As stated previously, the algorithm can be run by typing `python3 -m distalgo.runtime MIS.dis` or `run.py` on a *nix console.

These were some of the outputs produced during some trial runs of the algorithm using the graphs from MST:

### Graph 1

I re-used `graph-1` that I used for testing MST here. The following diagram depicts it (generated using _NetworkX_ and _matplotlib_):

![Test Case 1](https://raw.github.com/arjungmenon/Distributed-Graph-Algorithms/master/Maximal-Independent-Set/graph-1.png)

#### Run 1 (Solution: A, C, J, E)

    [2012-10-12 08:04:37,337]runtime:INFO: Creating instances of P..
    [2012-10-12 08:04:37,359]runtime:INFO: 11 instances of P created.
    [2012-10-12 08:04:37,367]runtime:INFO: Starting procs...
    [2012-10-12 08:04:37,369]P(A):INFO: A marked as VERTEX
    [2012-10-12 08:04:37,371]P(B):INFO: B marked as OUT
    [2012-10-12 08:04:37,372]P(F):INFO: F marked as OUT
    [2012-10-12 08:04:37,392]P(E):INFO: E marked as VERTEX
    [2012-10-12 08:04:37,393]P(I):INFO: I marked as OUT
    [2012-10-12 08:04:37,394]P(H):INFO: H marked as OUT
    [2012-10-12 08:04:37,394]P(G):INFO: G marked as OUT
    [2012-10-12 08:04:37,394]P(D):INFO: D marked as OUT
    [2012-10-12 08:04:37,406]P(C):INFO: C marked as VERTEX
    [2012-10-12 08:04:37,420]P(J):INFO: J marked as VERTEX
    [2012-10-12 08:04:37,455]P(0):INFO: Vertices in the MIS are: A, C, J, E
    [2012-10-12 08:04:37,458]runtime:INFO: ***** Statistics *****
    * Total procs: 11

#### Run 2 (Solution: C, J, F)

    [2012-10-12 08:06:04,921]runtime:INFO: Creating instances of P..
    [2012-10-12 08:06:04,948]runtime:INFO: 11 instances of P created.
    [2012-10-12 08:06:04,957]runtime:INFO: Starting procs...
    [2012-10-12 08:06:04,960]P(C):INFO: C marked as VERTEX
    [2012-10-12 08:06:04,962]P(D):INFO: D marked as OUT
    [2012-10-12 08:06:04,962]P(B):INFO: B marked as OUT
    [2012-10-12 08:06:04,962]P(I):INFO: I marked as OUT
    [2012-10-12 08:06:04,977]P(J):INFO: J marked as VERTEX
    [2012-10-12 08:06:04,978]P(H):INFO: H marked as OUT
    [2012-10-12 08:06:04,988]P(F):INFO: F marked as VERTEX
    [2012-10-12 08:06:04,989]P(E):INFO: E marked as OUT
    [2012-10-12 08:06:04,989]P(A):INFO: A marked as OUT
    [2012-10-12 08:06:04,989]P(G):INFO: G marked as OUT
    [2012-10-12 08:06:05,003]P(0):INFO: Vertices in the MIS are: C, J, F
    [2012-10-12 08:06:05,021]runtime:INFO: ***** Statistics *****
    * Total procs: 11

#### Run 3 (Solution: I, B, G)

    [2012-10-12 08:06:29,570]runtime:INFO: Creating instances of P..
    [2012-10-12 08:06:29,585]runtime:INFO: 11 instances of P created.
    [2012-10-12 08:06:29,596]runtime:INFO: Starting procs...
    [2012-10-12 08:06:29,597]P(G):INFO: G marked as VERTEX
    [2012-10-12 08:06:29,600]P(H):INFO: H marked as OUT
    [2012-10-12 08:06:29,600]P(E):INFO: E marked as OUT
    [2012-10-12 08:06:29,601]P(F):INFO: F marked as OUT
    [2012-10-12 08:06:29,619]P(B):INFO: B marked as VERTEX
    [2012-10-12 08:06:29,621]P(C):INFO: C marked as OUT
    [2012-10-12 08:06:29,621]P(A):INFO: A marked as OUT
    [2012-10-12 08:06:29,621]P(D):INFO: D marked as OUT
    [2012-10-12 08:06:29,634]P(I):INFO: I marked as VERTEX
    [2012-10-12 08:06:29,637]P(J):INFO: J marked as OUT
    [2012-10-12 08:06:29,671]P(0):INFO: Vertices in the MIS are: I, B, G
    [2012-10-12 08:06:29,674]runtime:INFO: ***** Statistics *****
    * Total procs: 11

#### Run 4 (Solution: H, B, F)

    [2012-10-12 08:06:41,018]runtime:INFO: Creating instances of P..
    [2012-10-12 08:06:41,034]runtime:INFO: 11 instances of P created.
    [2012-10-12 08:06:41,042]runtime:INFO: Starting procs...
    [2012-10-12 08:06:41,044]P(H):INFO: H marked as VERTEX
    [2012-10-12 08:06:41,046]P(E):INFO: E marked as OUT
    [2012-10-12 08:06:41,047]P(J):INFO: J marked as OUT
    [2012-10-12 08:06:41,047]P(I):INFO: I marked as OUT
    [2012-10-12 08:06:41,049]P(G):INFO: G marked as OUT
    [2012-10-12 08:06:41,066]P(B):INFO: B marked as VERTEX
    [2012-10-12 08:06:41,068]P(A):INFO: A marked as OUT
    [2012-10-12 08:06:41,068]P(C):INFO: C marked as OUT
    [2012-10-12 08:06:41,068]P(D):INFO: D marked as OUT
    [2012-10-12 08:06:41,083]P(F):INFO: F marked as VERTEX
    [2012-10-12 08:06:41,118]P(0):INFO: Vertices in the MIS are: H, B, F
    [2012-10-12 08:06:41,125]runtime:INFO: ***** Statistics *****
    * Total procs: 11

#### Run 5 (Solution: J, B, F)

    [2012-10-12 08:06:52,984]runtime:INFO: Creating instances of P..
    [2012-10-12 08:06:53,009]runtime:INFO: 11 instances of P created.
    [2012-10-12 08:06:53,016]runtime:INFO: Starting procs...
    [2012-10-12 08:06:53,018]P(B):INFO: B marked as VERTEX
    [2012-10-12 08:06:53,020]P(D):INFO: D marked as OUT
    [2012-10-12 08:06:53,020]P(C):INFO: C marked as OUT
    [2012-10-12 08:06:53,021]P(A):INFO: A marked as OUT
    [2012-10-12 08:06:53,042]P(J):INFO: J marked as VERTEX
    [2012-10-12 08:06:53,044]P(I):INFO: I marked as OUT
    [2012-10-12 08:06:53,044]P(H):INFO: H marked as OUT
    [2012-10-12 08:06:53,057]P(F):INFO: F marked as VERTEX
    [2012-10-12 08:06:53,059]P(G):INFO: G marked as OUT
    [2012-10-12 08:06:53,059]P(E):INFO: E marked as OUT
    [2012-10-12 08:06:53,086]P(0):INFO: Vertices in the MIS are: J, B, F
    [2012-10-12 08:06:53,090]runtime:INFO: ***** Statistics *****
    * Total procs: 11

#### Run 6 (Solution: A, H, C)

    [2012-10-12 08:10:02,800]runtime:INFO: Creating instances of P..
    [2012-10-12 08:10:02,816]runtime:INFO: 11 instances of P created.
    [2012-10-12 08:10:02,820]runtime:INFO: Starting procs...
    [2012-10-12 08:10:02,822]P(H):INFO: H marked as VERTEX
    [2012-10-12 08:10:02,823]P(E):INFO: E marked as OUT
    [2012-10-12 08:10:02,823]P(I):INFO: I marked as OUT
    [2012-10-12 08:10:02,823]P(G):INFO: G marked as OUT
    [2012-10-12 08:10:02,823]P(J):INFO: J marked as OUT
    [2012-10-12 08:10:02,832]P(C):INFO: C marked as VERTEX
    [2012-10-12 08:10:02,833]P(B):INFO: B marked as OUT
    [2012-10-12 08:10:02,833]P(D):INFO: D marked as OUT
    [2012-10-12 08:10:02,840]P(A):INFO: A marked as VERTEX
    [2012-10-12 08:10:02,840]P(F):INFO: F marked as OUT
    [2012-10-12 08:10:02,875]P(0):INFO: Vertices in the MIS are: A, H, C
    [2012-10-12 08:10:02,879]runtime:INFO: ***** Statistics *****
    * Total procs: 11

#### Run 7 (Solution: A, C, J, G)

    [2012-10-12 08:22:27,814]runtime:INFO: Creating instances of P..
    [2012-10-12 08:22:27,837]runtime:INFO: 11 instances of P created.
    [2012-10-12 08:22:27,846]runtime:INFO: Starting procs...
    [2012-10-12 08:22:27,847]P(C):INFO: C marked as VERTEX
    [2012-10-12 08:22:27,848]P(B):INFO: B marked as OUT
    [2012-10-12 08:22:27,848]P(D):INFO: D marked as OUT
    [2012-10-12 08:22:27,849]P(I):INFO: I marked as OUT
    [2012-10-12 08:22:27,859]P(A):INFO: A marked as VERTEX
    [2012-10-12 08:22:27,860]P(F):INFO: F marked as OUT
    [2012-10-12 08:22:27,870]P(J):INFO: J marked as VERTEX
    [2012-10-12 08:22:27,871]P(H):INFO: H marked as OUT
    [2012-10-12 08:22:27,878]P(G):INFO: G marked as VERTEX
    [2012-10-12 08:22:27,879]P(E):INFO: E marked as OUT
    [2012-10-12 08:22:27,892]P(0):INFO: Vertices in the MIS are: A, C, J, G
    [2012-10-12 08:22:27,897]runtime:INFO: ***** Statistics *****
    * Total procs: 11

#### Run 8 (Solution: I, B, F)

    [2012-10-14 05:37:02,765]runtime:INFO: Creating instances of P..
    [2012-10-14 05:37:02,781]runtime:INFO: 11 instances of P created.
    [2012-10-14 05:37:02,788]runtime:INFO: Starting procs...
    [2012-10-14 05:37:02,790]P(I):INFO: I marked as VERTEX
    [2012-10-14 05:37:02,792]P(J):INFO: J marked as OUT
    [2012-10-14 05:37:02,793]P(E):INFO: E marked as OUT
    [2012-10-14 05:37:02,793]P(D):INFO: D marked as OUT
    [2012-10-14 05:37:02,794]P(H):INFO: H marked as OUT
    [2012-10-14 05:37:02,796]P(C):INFO: C marked as OUT
    [2012-10-14 05:37:02,812]P(F):INFO: F marked as VERTEX
    [2012-10-14 05:37:02,814]P(G):INFO: G marked as OUT
    [2012-10-14 05:37:02,814]P(A):INFO: A marked as OUT
    [2012-10-14 05:37:02,827]P(B):INFO: B marked as VERTEX
    [2012-10-14 05:37:02,857]P(0):INFO: Vertices in the MIS are: I, B, F
    [2012-10-14 05:37:02,863]runtime:INFO: ***** Statistics *****
    * Total procs: 11

### Graph 2

Here I re-used `graph-2` from MST. This diagram depicts it (generated using _NetworkX_ and _matplotlib_):

![Test Case 2](https://raw.github.com/arjungmenon/Distributed-Graph-Algorithms/master/Maximal-Independent-Set/graph-2c.png)

#### Run 1 (Solution: A, J, L, G, D)

    [2012-10-14 05:39:41,343]runtime:INFO: Creating instances of P..
    [2012-10-14 05:39:41,363]runtime:INFO: 14 instances of P created.
    [2012-10-14 05:39:41,372]runtime:INFO: Starting procs...
    [2012-10-14 05:39:41,374]P(J):INFO: J marked as VERTEX
    [2012-10-14 05:39:41,375]P(I):INFO: I marked as OUT
    [2012-10-14 05:39:41,375]P(K):INFO: K marked as OUT
    [2012-10-14 05:39:41,375]P(H):INFO: H marked as OUT
    [2012-10-14 05:39:41,392]P(G):INFO: G marked as VERTEX
    [2012-10-14 05:39:41,393]P(E):INFO: E marked as OUT
    [2012-10-14 05:39:41,393]P(F):INFO: F marked as OUT
    [2012-10-14 05:39:41,404]P(A):INFO: A marked as VERTEX
    [2012-10-14 05:39:41,405]P(B):INFO: B marked as OUT
    [2012-10-14 05:39:41,423]P(L):INFO: L marked as VERTEX
    [2012-10-14 05:39:41,424]P(M):INFO: M marked as OUT
    [2012-10-14 05:39:41,439]P(D):INFO: D marked as VERTEX
    [2012-10-14 05:39:41,440]P(C):INFO: C marked as OUT
    [2012-10-14 05:39:41,454]P(0):INFO: Vertices in the MIS are: A, J, L, G, D
    [2012-10-14 05:39:41,468]runtime:INFO: ***** Statistics *****
    * Total procs: 14

#### Run 2 (Solution: I, K, B, G)

    [2012-10-14 05:40:23,968]runtime:INFO: Creating instances of P..
    [2012-10-14 05:40:23,989]runtime:INFO: 14 instances of P created.
    [2012-10-14 05:40:23,995]runtime:INFO: Starting procs...
    [2012-10-14 05:40:23,996]P(I):INFO: I marked as VERTEX
    [2012-10-14 05:40:23,997]P(E):INFO: E marked as OUT
    [2012-10-14 05:40:23,997]P(J):INFO: J marked as OUT
    [2012-10-14 05:40:23,997]P(H):INFO: H marked as OUT
    [2012-10-14 05:40:23,998]P(D):INFO: D marked as OUT
    [2012-10-14 05:40:23,998]P(C):INFO: C marked as OUT
    [2012-10-14 05:40:24,007]P(B):INFO: B marked as VERTEX
    [2012-10-14 05:40:24,008]P(A):INFO: A marked as OUT
    [2012-10-14 05:40:24,019]P(K):INFO: K marked as VERTEX
    [2012-10-14 05:40:24,020]P(M):INFO: M marked as OUT
    [2012-10-14 05:40:24,020]P(L):INFO: L marked as OUT
    [2012-10-14 05:40:24,030]P(G):INFO: G marked as VERTEX
    [2012-10-14 05:40:24,031]P(F):INFO: F marked as OUT
    [2012-10-14 05:40:24,063]P(0):INFO: Vertices in the MIS are: I, K, B, G
    [2012-10-14 05:40:24,069]runtime:INFO: ***** Statistics *****
    * Total procs: 14

#### Run 3 (Solution: A, J, M, D, G)

    [2012-10-14 05:40:43,620]runtime:INFO: Creating instances of P..
    [2012-10-14 05:40:43,641]runtime:INFO: 14 instances of P created.
    [2012-10-14 05:40:43,649]runtime:INFO: Starting procs...
    [2012-10-14 05:40:43,651]P(D):INFO: D marked as VERTEX
    [2012-10-14 05:40:43,652]P(I):INFO: I marked as OUT
    [2012-10-14 05:40:43,653]P(C):INFO: C marked as OUT
    [2012-10-14 05:40:43,653]P(E):INFO: E marked as OUT
    [2012-10-14 05:40:43,653]P(B):INFO: B marked as OUT
    [2012-10-14 05:40:43,671]P(M):INFO: M marked as VERTEX
    [2012-10-14 05:40:43,672]P(L):INFO: L marked as OUT
    [2012-10-14 05:40:43,672]P(K):INFO: K marked as OUT
    [2012-10-14 05:40:43,690]P(G):INFO: G marked as VERTEX
    [2012-10-14 05:40:43,691]P(H):INFO: H marked as OUT
    [2012-10-14 05:40:43,692]P(F):INFO: F marked as OUT
    [2012-10-14 05:40:43,704]P(A):INFO: A marked as VERTEX
    [2012-10-14 05:40:43,718]P(J):INFO: J marked as VERTEX
    [2012-10-14 05:40:43,742]P(0):INFO: Vertices in the MIS are: A, J, M, D, G
    [2012-10-14 05:40:43,753]runtime:INFO: ***** Statistics *****
    * Total procs: 14

#### Run 4 (Solution: C, J, L, F)

    [2012-10-14 05:41:55,466]runtime:INFO: Creating instances of P..
    [2012-10-14 05:41:55,487]runtime:INFO: 14 instances of P created.
    [2012-10-14 05:41:55,492]runtime:INFO: Starting procs...
    [2012-10-14 05:41:55,494]P(J):INFO: J marked as VERTEX
    [2012-10-14 05:41:55,496]P(K):INFO: K marked as OUT
    [2012-10-14 05:41:55,496]P(I):INFO: I marked as OUT
    [2012-10-14 05:41:55,497]P(H):INFO: H marked as OUT
    [2012-10-14 05:41:55,512]P(F):INFO: F marked as VERTEX
    [2012-10-14 05:41:55,512]P(E):INFO: E marked as OUT
    [2012-10-14 05:41:55,512]P(G):INFO: G marked as OUT
    [2012-10-14 05:41:55,513]P(A):INFO: A marked as OUT
    [2012-10-14 05:41:55,525]P(L):INFO: L marked as VERTEX
    [2012-10-14 05:41:55,527]P(M):INFO: M marked as OUT
    [2012-10-14 05:41:55,541]P(C):INFO: C marked as VERTEX
    [2012-10-14 05:41:55,543]P(D):INFO: D marked as OUT
    [2012-10-14 05:41:55,543]P(B):INFO: B marked as OUT
    [2012-10-14 05:41:55,579]P(0):INFO: Vertices in the MIS are: C, J, L, F
    [2012-10-14 05:41:55,584]runtime:INFO: ***** Statistics *****
    * Total procs: 14

#### Run 5 (Solution: M, J, B, E)

    [2012-10-14 05:42:42,365]runtime:INFO: Creating instances of P..
    [2012-10-14 05:42:42,386]runtime:INFO: 14 instances of P created.
    [2012-10-14 05:42:42,395]runtime:INFO: Starting procs...
    [2012-10-14 05:42:42,396]P(E):INFO: E marked as VERTEX
    [2012-10-14 05:42:42,397]P(F):INFO: F marked as OUT
    [2012-10-14 05:42:42,398]P(I):INFO: I marked as OUT
    [2012-10-14 05:42:42,398]P(H):INFO: H marked as OUT
    [2012-10-14 05:42:42,398]P(D):INFO: D marked as OUT
    [2012-10-14 05:42:42,398]P(G):INFO: G marked as OUT
    [2012-10-14 05:42:42,416]P(M):INFO: M marked as VERTEX
    [2012-10-14 05:42:42,418]P(L):INFO: L marked as OUT
    [2012-10-14 05:42:42,418]P(K):INFO: K marked as OUT
    [2012-10-14 05:42:42,438]P(B):INFO: B marked as VERTEX
    [2012-10-14 05:42:42,440]P(C):INFO: C marked as OUT
    [2012-10-14 05:42:42,440]P(A):INFO: A marked as OUT
    [2012-10-14 05:42:42,455]P(J):INFO: J marked as VERTEX
    [2012-10-14 05:42:42,486]P(0):INFO: Vertices in the MIS are: M, J, B, E
    [2012-10-14 05:42:42,489]runtime:INFO: ***** Statistics *****
    * Total procs: 14

### Note
Many more solutions different from the ones listed above were found for each graph, but they've been omitted for brevity's sake.

---