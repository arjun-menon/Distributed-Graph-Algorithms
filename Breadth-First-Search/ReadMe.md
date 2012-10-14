Distributed Breadth First Search
================================

Overview
--------

The goal of the algorithm is to distribute the task of checking whether an element exists in a given tree to multiple processes. The entire program is contained in one file: `BFS.dis`. This is how you would run the program, and these are the command-line options offered by the program:

`python3 -m distalgo.runtime BFS.dis [num_procs] [elem_to_search] [r height]`

The first two command line options allow the user to select the number of worker processes that should be started, and the element that is to be searched for. By `default num_procs = 4` and `elem_to_search = 300`.

A graph library [1] known as NetworkX was used in this project. It is a well-renown pure Python library that provides several useful features pertaining to graphs. Granted, it was a bit unnecessary for this project, but I was anticipating more use for it than was needed.

Initially the algorithm uses NetworkX to construct a large tree. NetworkX offers a bunch of graph generating algorithms [2], few of which generate trees. The particular type of tree generator used was a *“perfectly balanced r-tree of height h”*. By default the tree constructed is of `r = 4` and `height = 4`. The user can opt to re-construct the NetworkX balanced tree with a different ‘r’ and ‘height’ parameters by specifying the last two command line options. It is necessary to specify all four command line options to reconfigure the tree.

Situation
---------

Searching online for distributed breadth first search algorithms brings up algorithms that are primarily designed for distributed memory systems. These are systems like Blue Gene et al. where we have multiple computers working in cohesion to tackle a problem. The only “shared” memory they have in this case would probably be a massive RAID array. However the latency to access this RAID system would make any algorithm that primarily hinges on a fast shared read-only memory inefficient/unusable.

DistAlgo however allows the processes to access shared global variables read-only. This makes sense on small distributed systems such as the multi-core or multi-processor computer. In such systems, the RAM is shared between the processors so reading shared data is a non-issue. (Issues arise when we write to data shared by CPUs - such as cache cohesion, e.t.c.)

In DistAlgo’s case, the shared read-only memory feature was very suitable to the problem at hand. The algorithm I used is of my own invention. The path to solving this problem in a distributed manner became very obvious to me in a few minutes of thinking. The algorithm makes good use of the fact that the _graph is in a *tree structure*_ along with DistAlgo’s shared read-only memory feature. Instead of passing around chunks of the tree, it simply passes a node, representing a sub-tree to other processes. Processes work in parallel to prune the tree and find the element being looked for. A detailed description of the algorithm can be found below.

Detailed Algorithm Description
------------------------------

The tree itself is a shared data structure. No one writes to the tree or modifies it in anyway. The tree is frozen before the processes are setup. Due to the read-only nature of the tree any type of mediation is unnecessary here.

In this algorithm, each process has a queue. This queue contains a set of nodes to be inspected. This queue is called the ‘work queue’. Initially the work queue of all but the first process is empty. Right before the processes start, the main function pushes the root node of the tree onto the first process’ queue.

Every process with a non-empty work queue (initially only process 0) starts out by popping an element from its queue and inspecting it. If the element turns out not to be the element being searched for, then the process adds all the child nodes (if any) of the recently inspected element to the queue.

The rest of the processes; lacking any work to do (due to their work queue being empty), broadcast a request for work to all of the other processes. In response to this request for work, every process that has a work queue with 2 or more elements replies by popping an element from its work queue and sending it _unexamined_ to the process requesting work. Initially, Process 0 is the only process with a non-empty work queue – consequently it is process 0 that hands out (“distributes”) the work to all of the other processes.

So initially all of the other processes quickly receive a node each from process 0. Then, each process, on its own begins to examine the node that they currently have in the breadth-first-search manner. As such, the tree has been divided into a several chunks among the processes and all of them are going through it in parallel.

In due course, one of the processes might reach the leaf nodes of the chunk of the tree that was given to it. When this happens, the process ends up with an empty work queue, and it once again sends out requests for work to all of the processes. This time unlike before, it could potentially receive up to *n-1* replies with a node each since all processes could potentially have a non-empty work queue. The fact that it received more than one reply however should not have any adverse affect on the performance of the algorithm. On the contrary, it should reduce the likelihood of an imminent successive request for work by the same process.

When a process eventually encounters a node that matches the value of the element being searched for, the process marks itself as “completed” and immediately sends out a notification to all other processes of “completion.” Subsequently all other processes receive this notification and mark themselves as “completed”. `completed` here is a Boolean private to each process which ceases the execution of the process. When `BFS.dis` is run, you can see special output made by the processes when it reaches the completion stage.

The other alternate termination state is that, the element was not found in the tree. When this happens it is not as easy for each process to know that the tree has been completely pruned since they’re all working on separate chunks of the tree. The algorithm handles this problem by using a set variable called “unserviced” private to each process. Anytime a process receives a request for work from another process and is unable to service it, it adds that process to this set. When the case of element not being found occurs, every process begins to starve – since all of their work queues run dry. When this happens, the size of the “unserviced” set slowly builds up. The same DistAlgo `await` condition that waits for work or completion, also checks if the number of unserviced processes = the number of other processes. When this condition is satisfied it knows that the search was unsuccessful and the element is not in the graph.

Testing & Caveats
-----------------
I’ve tested the BFS algorithm with varying tree sizes, varying number of processes and varying search targets. Sample test cases can be seen named `BFS_test_run_2.txt`, `BFS_test_run_2.txt`, e.t.c.

Overall, with sane values for these variables; the BFS search works fine and does what it’s supposed to do. However I’ve occasionally  run into a hiccup or two, when handling large tree sizes. This is because currently DistAlgo has a limit on how large the size of a message send between processes can be. The way the algorithm works; in response to a work request, it sends along with a node a list of all nodes it has visited so far. Currently as the tree size grows larger; one can see dropped packets in communication between nodes. Whereas an `r=4, height=4` tree has `341` nodes, an `r=4, height=5` tree has `1365` nodes -- the tree size grows exponentially with r and height increasing. With large tree sizes, more often than not we see dropped packets. The algorithm was not designed to tolerate packet loss, so in such circumstances the behavior of the algorithm is undefined.