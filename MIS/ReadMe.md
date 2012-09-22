Overview
========

This algorithm is largely based on the sequential MST algorithm.


Conditions and Constraints
--------------------------
    a. Each node in the graph is represented by a process.

    b. A process/node can only communicate with other processes/nodes 
       that it has an edge with. Although DistAlgo allows a process to 
       communicate with any other process, this constraint has been 
       articially imposed upon this algorithm to imiate real-life 
       networks where there isn't necessarily a communication link 
       between every computer with every other computer.

    c. There's a special process known as the Control Process. The 
       Control Process fulfills three roles: (1) It iniates the algorithm.
       (2) It collects output. (3) It terminates the algorithm.

       The control process is not bound by constraint (a), and any process is 
       permitted to communicate to it and it to all other processes. However, 
       ehe control process isn't absolutely necessary to the algorithm, or a 
       crucial component of it. The initation of the algorithm could be moved to 
       top-level main() function, and rather than collect output, each node could 
       produce output declaring itself as a vertex of the MST (it does this already), 
       and termination could be handled by the last VERTEX node; albeit in a less
       elegant fashion. The control process is overall just a niceity that simplifies 
       and renders more elegant this particular implementation.


High-Level Overview of the Algorithm
------------------------------------
Each node/process can have one of 3 states: NORMAL, VERTEX, OUT.
Initally each node is NORMAL.

The algorithm follows the idea behind the sequential algorithm, and 
does the following:

    a. Picks a random node in the graph.
    b. Marks that node as a VERTEX, and the its neighbors as OUT.
    c. Looks for another node in the graph that is NORMAL (ie. not a VERTEX and not OUT)
    d. It repeats from step a, except instead of a random node, it's the node from step c.
    e. The base case, is when in step c, no NORMAL node could be found. When this happens, 
       the algorithm terminates.


Some details about the implementation
-------------------------------------

Key functions:

Overview of mark():
        * Marks a node as VERTEX,
        * Sends messages to neighboring nodes telling them to mark themselves as OUT.
        * Initiates a search for the next NORMAL node in the graph.
        * If none could be found, informs the Control Process that the algorithm is finished.

OnSearch(path), search(path, source), OnSearchReply(path):

        These functions together sweep through the graph in search for a NORMAL node.

        Initially, the search is kickstarted by mark(). `mark` directly 
        calls `search`. `search` then sends message to all its neighboring 
        nodes, asking them to participate in the search. `search`also waits 
        for replies from _all_ its neighboring nodes before doing anything 
        else. The `path` parameter of `search` allows it to keep a record of 
        the path to be taken to reach it from the marked node. This is used  
        later on by the marked node. The `search` function eventually, after the 
        completion of the search, returns a "path list": a list of paths leading 
        to all NORMAL nodes from the marked node.

        Each invocation of `search` is accompanied with a `path` from the initial 
        marked node to that particular node. At the beginning the `path` is `None`, 
        but for subsequent `search`es, the `path` paramter contains a list of nodes, 
        which lists the path to be taken to reach node X from the marked node.

        Each time a node is notified to join the search via the message `Search` 
        handled by `OnSearch`, the node checks if it is already pariticpating in a 
        search by that particular marked node (the one that iniated the search.)
        It does so by keeping a record of all the searches it has participated in, 
        in the set veriable `search_requested`. If a search request comes from a node 
        to "re-participate" in the search its already paritipating it, it effectively 
        rejects that request, by sending a reply consisting on an empty path list.

        Every time the `search` function realizes its own state is NORMAL, it adds 
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

More on mark() and the Control Process:

        The marked node, upon receiving the reply, picks a random path out of the path list, and 
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

        The control process also prints out a list of all the vertices 
        once more (although this could be inferred from the individual 
        output produced by each process as they got marked.) This is 
        accomplished by means of a `Marked` message sent by each process/node 
        when it gets marked as VERTEX or OUT. This feature accomplishes 
        purpose (2) of the control process: output collection.
