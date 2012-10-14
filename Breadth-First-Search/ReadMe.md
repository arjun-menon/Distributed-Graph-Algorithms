Distributed Breadth First Search
================================

Overview
--------

The goal of the algorithm is to distribute the task of checking whether an element exists in a given tree to multiple processes. Unlike the other algorithms in this project, this one follows a _processes as workers_ model.

### The processes-as-workers model

Normally a distributed graph algorithm means an algorithm where each node in the graph represents a process and the key challenge is to execute an otherwise simple sequential algorithm over distributed processes where _communication between nodes is ***restricted*** to nodes that have an edge between them_. This processes-as-nodes model is useful as it models real-world systems of networked computers. Hadoop and DHT are two examples of commonly used systems that fit this model However, at the same time, there is also a lot of application for another model: One where we break down a large workload into smaller chunks and try to get them done faster using multiple computers.

One could guess there is a lot more application for this model. On supercomputers the goal is to solve a problem faster. Applications today try to use more cores on a computer and run into the same challenge: breaking down problems to solve them faster in parallel. BOINC and Folding@Home are two well-known projects that allow home computer users to donate their idle CPU time to solve real-world problems. So this is an area with lots of great applications and is definitely worth exploring.

As a side note, solving BFS using the processes-as-nodes model would be very trivial. Both the Shortest Path algorithm and MIS, already contains a search very similar to BFS in them.

### Context to my algorithm

I designed this algorithm myself. The algorithm uses a kind-of workload balancing technique; where first one process starts with "all" of the workload, and then n-1 processes ping this one process for work. It then distributes chunks of its work to each of these processes. (The _"chunk"_ of work here is a chunk of a tree -- or rather, a subtree.) Eventually some process finishes working on its chunk, asks for more work, gets it, and keeps on working. This continues until every process runs out of work and is unable to get any from the others. When this happens, the processes terminate. 

One **crucial feature** that this algorithm relies on is: _common shared memory._ Common shared memory is not something that is always available in a system. Even if and when it is available there are often serious constraints on how it can be used. Three common situations exist:

1. On supercomputers, clusters and large-scale servers there is usually some “shared” memory -- generally in the form of a massive RAID array. However the latency to access this RAID system would make any algorithm that primarily hinges on a fast shared read-only memory inefficient and unusable.
2. On systems like BOINC or Folding@Home, there is absolutely no easily-accessible shared memory. A workload is shipped to the user's computers, and until the user is done working on it; there is no more communication with the server (workload dispenser.)
3. Finally, we have a much more common system: modern multi-core computers. On multi-care, there ***is*** shared memory. It usually exists at multiple levels: Cache memory (L-2 cache and L-3 cache) -> Main memory (RAM) -> Secondary storage (SSD/HDD) -> Tertiary storage (tape backup, etc.) Tertiary is uncommon, but the others are all common.

The processes-as-workers model _with shared memory_ works best in the last situation. Generaly on a multi-core computer, there is local storage *at each* core -- registers and L-1 cahce. Then, there's cache shared between the cores: L-2 and L-3. After that we have RAM, and so on.

Even though the cores share a common memory like L-2 cache, the CPU handles all the trouble of maintatin its integrity, i.e. handling cache conflicts and maintaining cache collisions. THis is usally handled by a marking a segment of a cahce as _dirty_ when its been written to in its L-1 mirror by some core. Then when a different core tries to read it, the CPU updates the value on L-2 to mirror the newer L-1 value.

The result of all this is, it gives programmers the same experience writing programs on multi-core systems as they had writing multi-threaded programs on single-core computers. Needless to say, it's not a very good experience. There is a solution to this however. Forget writing to shared memory -- only read from it. With _shared ***read-only*** memory we can mitigate cache cohesion and related problems. In [Andrew Tanenbaum](https://en.wikipedia.org/wiki/Andrew_Tanenbaum)'s book on [Operating Systems](http://www.amazon.com/Operating-Systems-Design-Implementation-Edition/dp/0136386776), he talks about microkernels, where every little piece of the OS runs in its own little process. They communicate with each other just as in a distributed system.

In DistAlgo, we can model this situation _very well_. When we create new processes in DistAlgo, _all the global context is ***copied***_ into every process (based on my understanding.) In a more efficient the variables would not be copied, but rather be _shared read-only_ at the OS-level, but our main interest here is to create an exemplary prototype rather than a deployable implementation.

Implementation
--------------

### Usage

The algorithm is contained in one file: `BFS.dis.py`. It can be run using `run.py` or using DistAlgo directly like this: `python3 -m distalgo.runtime BFS.dis`. The program offers the following options (disaplyed using the `-h` optarg):

	usage: BFS.dis [-h] [-w WORKERS] [-e ELEMENT] [-r RFACTOR] [-x XHEIGHT]

	Perform breadth-first search in paralell using several workers.

	optional arguments:
	  -h, --help            show this help message and exit
	  -w WORKERS, --workers WORKERS
	                        Number of workrrs. [Default 4]
	  -e ELEMENT, --element ELEMENT
	                        The element to search for. [Default 300]
	  -r RFACTOR, --rfactor RFACTOR
	                        r factor in the NetworkX generated perfectly balanced
	                        r-tree of height h. [Default 4]
	  -x XHEIGHT, --xheight XHEIGHT
	                        Height of the Network generated perfectly balanced
	                        r-tree of height h. [Default 4]

The first two command line options allow the user to select the number of worker processes that should be started, and the element that is to be searched for. By default the number of workers is `4` and the element to search for is `300`.

The next two options have to do with the random tree that is constructed. The algorithm initially uses NetworkX to construct a large tree. NetworkX offers a [bunch of graph generating algorithms](http://networkx.lanl.gov/reference/generators.html); some of which generate trees. The type of NewtworkX tree generator that I used was the *“perfectly balanced r-tree of height h” generator*. The factor `r` and the height `h` determine the size of the tree. By default r is `4` and height `4`. The user can construct the NetworkX balanced tree with different `r` and `height` parameters by specifying the last two command line options.

Detailed Algorithm Description
------------------------------
The algorithm makes good use of the fact that the _graph is in a *tree structure*_ along with DistAlgo’s shared read-only memory feature. Instead of passing around chunks of the tree, it simply passes a node, representing a sub-tree to other processes. Processes work in parallel to prune the tree and find the element being looked for. A detailed description of the algorithm can be found below.

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
When run, each node prints a message for each node it inspects. It also prints messages when it requests work from another process, receives a request for work, gets work, etc.

The following a few sample _truncated_ test runs of the algorithm:

#### Sample Test Run (./run.py -r 3 -e 100)

	Using 4 workers to search for the element 100 using BFS in a r-3 height-4 tree containing 121 nodes.
	[2012-10-14 15:10:41,526]runtime:INFO: Creating instances of P..
	[2012-10-14 15:10:41,532]runtime:INFO: 4 instances of P created.
	[2012-10-14 15:10:41,538]runtime:INFO: Starting procs...
	[2012-10-14 15:10:41,538]P(1):INFO: Empty queue; sending requests for work
	[2012-10-14 15:10:41,538]P(2):INFO: Empty queue; sending requests for work
	[2012-10-14 15:10:41,538]P(3):INFO: Empty queue; sending requests for work
	[2012-10-14 15:10:41,538]P(0):INFO: Inspected 0
	[2012-10-14 15:10:41,539]P(0):INFO: Inspected 1
	[2012-10-14 15:10:41,540]P(0):INFO: Inspected 2
	[2012-10-14 15:10:41,540]P(0):INFO: Inspected 3
	[2012-10-14 15:10:41,541]P(0):INFO: Inspected 4
	[2012-10-14 15:10:41,541]P(0):INFO: Inspected 5
	[2012-10-14 15:10:41,542]P(0):INFO: Inspected 6
	[2012-10-14 15:10:41,542]P(1):INFO: Received request for work from 2
	[2012-10-14 15:10:41,542]P(1):INFO: Received request for work from 3
	[2012-10-14 15:10:41,542]P(3):INFO: Received request for work from 1
	[2012-10-14 15:10:41,542]P(2):INFO: Received request for work from 3
	[2012-10-14 15:10:41,542]P(0):INFO: Inspected 8
	[2012-10-14 15:10:41,542]P(2):INFO: Received request for work from 1
	[2012-10-14 15:10:41,543]P(3):INFO: Received request for work from 2
	[2012-10-14 15:10:41,543]P(0):INFO: Received request for work from 1
	[2012-10-14 15:10:41,543]P(0):INFO: Giving work [9] to 1
	[2012-10-14 15:10:41,544]P(0):INFO: Received request for work from 2
	[2012-10-14 15:10:41,544]P(0):INFO: Giving work [7] to 2
	[2012-10-14 15:10:41,544]P(1):INFO: Got work [9] from 0
	[2012-10-14 15:10:41,544]P(0):INFO: Received request for work from 3
	[2012-10-14 15:10:41,545]P(0):INFO: Giving work [10] to 3
	[2012-10-14 15:10:41,545]P(1):INFO: Inspected 9
	[2012-10-14 15:10:41,545]P(0):INFO: Inspected 11
	[2012-10-14 15:10:41,545]P(2):INFO: Got work [7] from 0
	[2012-10-14 15:10:41,545]P(0):INFO: Inspected 12
	[2012-10-14 15:10:41,545]P(1):INFO: Inspected 28
	[2012-10-14 15:10:41,545]P(0):INFO: Inspected 13
	[2012-10-14 15:10:41,545]P(2):INFO: Inspected 7
	[2012-10-14 15:10:41,546]P(0):INFO: Inspected 14
	[2012-10-14 15:10:41,545]P(3):INFO: Got work [10] from 0
	[2012-10-14 15:10:41,546]P(0):INFO: Inspected 15
	[2012-10-14 15:10:41,546]P(1):INFO: Inspected 29
	...
	[2012-10-14 15:10:41,549]P(1):INFO: Inspected 92
	[2012-10-14 15:10:41,549]P(3):INFO: Element 100 found. BFS Completed!!!
	[2012-10-14 15:10:41,549]P(0):INFO: Inspected 45
	[2012-10-14 15:10:41,549]P(0):INFO: Inspected 48
	[2012-10-14 15:10:41,549]P(2):INFO: Inspected 72
	[2012-10-14 15:10:41,549]P(1):INFO: Inspected 93
	[2012-10-14 15:10:41,549]P(0):INFO: Inspected 46
	[2012-10-14 15:10:41,549]P(0):INFO: Inspected 47
	[2012-10-14 15:10:41,550]P(0):INFO: Inspected 49
	[2012-10-14 15:10:41,550]P(0):INFO: Inspected 50
	[2012-10-14 15:10:41,550]P(2):INFO: Inspected 70
	[2012-10-14 15:10:41,550]P(1):INFO: Empty queue; sending requests for work
	[2012-10-14 15:10:41,550]P(0):INFO: Received notice that 3 found elem 100. Terminating!
	[2012-10-14 15:10:41,550]P(2):INFO: Inspected 71
	[2012-10-14 15:10:41,550]P(2):INFO: Empty queue; sending requests for work
	[2012-10-14 15:10:41,552]P(1):INFO: Received notice that 3 found elem 100. Terminating!
	[2012-10-14 15:10:41,558]P(2):INFO: Received notice that 3 found elem 100. Terminating!
	[2012-10-14 15:10:41,562]runtime:INFO: ***** Statistics *****
	* Total procs: 4

In this run, the element `100` was found by process number `3`.

#### Sample Test Run (./run.py -r 3)

	Using 4 workers to search for the element 300 using BFS in a r-3 height-4 tree containing 121 nodes.
	[2012-10-14 15:10:15,463]runtime:INFO: Creating instances of P..
	[2012-10-14 15:10:15,469]runtime:INFO: 4 instances of P created.
	[2012-10-14 15:10:15,475]runtime:INFO: Starting procs...
	[2012-10-14 15:10:15,475]P(3):INFO: Empty queue; sending requests for work
	[2012-10-14 15:10:15,476]P(1):INFO: Empty queue; sending requests for work
	[2012-10-14 15:10:15,476]P(0):INFO: Inspected 0
	[2012-10-14 15:10:15,476]P(2):INFO: Empty queue; sending requests for work
	[2012-10-14 15:10:15,476]P(0):INFO: Inspected 1
	[2012-10-14 15:10:15,477]P(0):INFO: Inspected 2
	[2012-10-14 15:10:15,478]P(0):INFO: Inspected 3
	[2012-10-14 15:10:15,478]P(0):INFO: Inspected 4
	[2012-10-14 15:10:15,478]P(3):INFO: Received request for work from 2
	[2012-10-14 15:10:15,479]P(1):INFO: Received request for work from 3
	[2012-10-14 15:10:15,479]P(0):INFO: Received request for work from 3
	[2012-10-14 15:10:15,479]P(3):INFO: Received request for work from 1
	[2012-10-14 15:10:15,479]P(0):INFO: Giving work [5] to 3
	[2012-10-14 15:10:15,479]P(1):INFO: Received request for work from 2
	[2012-10-14 15:10:15,479]P(2):INFO: Received request for work from 1
	[2012-10-14 15:10:15,480]P(2):INFO: Received request for work from 3
	[2012-10-14 15:10:15,480]P(3):INFO: Got work [5] from 0
	[2012-10-14 15:10:15,481]P(0):INFO: Received request for work from 2
	[2012-10-14 15:10:15,481]P(3):INFO: Inspected 5
	[2012-10-14 15:10:15,481]P(0):INFO: Giving work [6] to 2
	[2012-10-14 15:10:15,481]P(3):INFO: Inspected 16
	[2012-10-14 15:10:15,482]P(3):INFO: Inspected 17
	[2012-10-14 15:10:15,482]P(3):INFO: Inspected 18
	[2012-10-14 15:10:15,482]P(0):INFO: Received request for work from 1
	[2012-10-14 15:10:15,482]P(2):INFO: Got work [6] from 0
	[2012-10-14 15:10:15,482]P(0):INFO: Giving work [8] to 1
	[2012-10-14 15:10:15,482]P(3):INFO: Inspected 49
	[2012-10-14 15:10:15,483]P(2):INFO: Inspected 6
	...
	[2012-10-14 15:10:15,524]P(0):INFO: Received request for work from 3
	[2012-10-14 15:10:15,524]P(2):INFO: Inspected 115
	[2012-10-14 15:10:15,524]P(1):INFO: Got work [117] from 0
	[2012-10-14 15:10:15,525]P(0):INFO: Giving work [120] to 3
	[2012-10-14 15:10:15,525]P(2):INFO: Empty queue; sending requests for work
	[2012-10-14 15:10:15,525]P(1):INFO: Inspected 117
	[2012-10-14 15:10:15,525]P(1):INFO: Empty queue; sending requests for work
	[2012-10-14 15:10:15,525]P(0):INFO: Inspected 118
	[2012-10-14 15:10:15,526]P(3):INFO: Got work [120] from 0
	[2012-10-14 15:10:15,526]P(0):INFO: Received request for work from 2
	[2012-10-14 15:10:15,526]P(3):INFO: Received request for work from 2
	[2012-10-14 15:10:15,526]P(1):INFO: Received request for work from 2
	[2012-10-14 15:10:15,526]P(0):INFO: Inspected 119
	[2012-10-14 15:10:15,526]P(0):INFO: Received request for work from 1
	[2012-10-14 15:10:15,527]P(0):INFO: Empty queue; sending requests for work
	[2012-10-14 15:10:15,527]P(3):INFO: Received request for work from 1
	[2012-10-14 15:10:15,527]P(2):INFO: Received request for work from 1
	[2012-10-14 15:10:15,527]P(3):INFO: Inspected 120
	[2012-10-14 15:10:15,527]P(2):INFO: Received request for work from 0
	[2012-10-14 15:10:15,527]P(1):INFO: Received request for work from 0
	[2012-10-14 15:10:15,527]P(2):INFO: Unable to get work. Assuming element 300 not in tree. Terminating... 
	[2012-10-14 15:10:15,527]P(3):INFO: Received request for work from 0
	[2012-10-14 15:10:15,528]P(1):INFO: Unable to get work. Assuming element 300 not in tree. Terminating... 
	[2012-10-14 15:10:15,528]P(3):INFO: Empty queue; sending requests for work
	[2012-10-14 15:10:15,528]P(3):INFO: Unable to get work. Assuming element 300 not in tree. Terminating... 
	[2012-10-14 15:10:15,529]P(0):INFO: Received request for work from 3
	[2012-10-14 15:10:15,529]P(0):INFO: Unable to get work. Assuming element 300 not in tree. Terminating... 
	[2012-10-14 15:10:15,533]runtime:INFO: ***** Statistics *****
	* Total procs: 4

This test run is on an identical tree as the previous one, but instead looks out for the (non-existent) element `300`. As each process is work-starved it terminates itself. The result (shown above) means the node does not exist in the tree.

### More Test Runs
I have conducted more test runs of this algorithm with varying tree sizes, number of processes search targets. Due to the long size of the resulting output they have been stored in separate files. These test cases can be found in the files named `BFS_test_run_*.txt` in this directory. _Note:_ the command-line arguments for those test runs differ from the current style, because I had not used `argparse` when I first implemented the algorithm. However the defaults back then were the same as the ones now.

### Caveats

Overall, with medium-sized trees (about a thousands nodes); this BFS algorithm works fine and does what it’s supposed to do. However when handling large tree sizes, it may or may not run into problems. This is because currently DistAlgo has a limit on how large the size of a message send between processes can be. The way the algorithm is implemented; in response to a work request, it sends a list of all nodes it has visited so far. The tree generated increases in size exponentially as `r` and `height` is increased. Whereas with `r=4, height=4`, the tree has `341` nodes; with `r=4` and `height=5` the tree has `1365` nodes. As such, as the tree size grows larger; one can see dropped packets between nodes randomly. The algorithm does not take packet loss into consideration, so when it occurs the behavior of the algorithm is undefined.

---