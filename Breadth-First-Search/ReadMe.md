Distributed Breadth First Search
================================

Overview
--------

The goal of the algorithm is to distribute the task of checking whether an element exists in a given graph to multiple processes. Unlike the other algorithms in this project, this one follows a _processes as workers_ model.

### The processes-as-workers model

Normally a distributed graph algorithm means an algorithm where each node in the graph represents a process and the key challenge is to execute an otherwise simple sequential algorithm over distributed processes where _communication between nodes is ***restricted*** to nodes that have an edge between them_. This processes-as-nodes model is useful as it models real-world systems of networked computers. Hadoop and DHT are two examples of commonly used systems that fit this model However, at the same time, there is also a lot of application for another model: One where we break down a large workload into smaller chunks and try to get them done faster using multiple computers.

One could guess there is a lot more application for this model. On supercomputers the goal is to solve a problem faster. Applications today try to use more cores on a computer and run into the same challenge: breaking down problems to solve them faster in parallel. BOINC and Folding@Home are two well-known projects that allow home computer users to donate their idle CPU time to solve real-world problems. So this is an area with lots of great applications and is definitely worth exploring.

As a side note, solving BFS using the processes-as-nodes model would be very trivial. Both the Shortest Path algorithm and MIS, already contains a search very similar to BFS in them.

### Context to my algorithm

I designed this algorithm myself. The algorithm uses a kind-of workload balancing technique; where first one process starts with "all" of the workload, and then n-1 processes ping this one process for work. It then distributes chunks of its work to each of these processes. (The _"chunk"_ of work here is a chunk of a graph -- or rather, a subgraph.) Eventually some process finishes working on its chunk, asks for more work, gets it, and keeps on working. This continues until every process runs out of work and is unable to get any from the others. When this happens, the processes terminate. 

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

	usage: BFS.dis [-h] [-w WORKERS] [-n NODES] [-e EDGES]

	Perform breadth-first search on a random graph in paralell using several
	workers.

	optional arguments:
	  -h, --help            show this help message and exit
	  -w WORKERS, --workers WORKERS
	                        Number of workers to do the search. [Default 4]
	  -n NODES, --nodes NODES
	                        The maximum number of nodes in the random graph. [Default 6]
	  -e EDGES, --edges EDGES
	                        The number of edges to in the random graph. [Default 10]

The first command line option allows the user to select the number of worker processes that should be started. The next two control the nature of the random graph generated by `graph_gen.py`. Tinker with those values to produces different sized graphs and control its connectedness.

Detailed Algorithm Description
------------------------------
The algorithm performs a traditional breadth-first search at every node, but also tries to distribute the workload of sweeping through the graph evenly to all processes/workers. Instead of passing around chunks of the graph, it simply passes an un-inspected node to other processes. This node could itself point to other nodes and so on recursively -- so the other process effectively has a sub-graph to work on. It is only when the a process has run into leaf nodes (in the case of a tree), or graph with no more unvisited neighboring edges, does it run out of work. The processes thus work in parallel to prune the graph and find the element being looked for. More details on the algorithm can be found below.

The graph itself is a shared data structure. No one writes to the graph or modifies it in anyway. The graph is frozen before the processes are setup. Due to the read-only nature of the graph any type of mediation is unnecessary here.

In this algorithm, each process has a queue. This queue contains a set of nodes to be inspected. This queue is called the ‘work queue’. Initially the work queue of all but the first process is empty. Right before the processes start, the main function pushes the root node of the graph onto the first process’ queue.

Every process with a non-empty work queue (initially only process 0) starts out by popping an element from its queue and inspecting it. If the element turns out not to be the element being searched for, then the process adds all the child nodes (if any) of the recently inspected element to the queue.

The rest of the processes; lacking any work to do (due to their work queue being empty), broadcast a request for work to all of the other processes. In response to this request for work, every process that has a work queue with 2 or more elements replies by popping an element from its work queue and sending it _unexamined_ to the process requesting work. Initially, Process 0 is the only process with a non-empty work queue – consequently it is process 0 that hands out (“distributes”) the work to all of the other processes.

So initially all of the other processes quickly receive a node each from process 0. Then, each process, on its own begins to examine the node that they currently have in the breadth-first-search manner. As such, the graph has been divided into a several chunks among the processes and all of them are going through it in parallel.

In due course, one of the processes might reach the leaf nodes of the chunk of the graph that was given to it. When this happens, the process ends up with an empty work queue, and it once again sends out requests for work to all of the processes. This time unlike before, it could potentially receive up to *n-1* replies with a node each since all processes could potentially have a non-empty work queue. The fact that it received more than one reply however should not have any adverse affect on the performance of the algorithm. On the contrary, it should reduce the likelihood of an imminent successive request for work by the same process.

When a process eventually encounters a node that matches the value of the element being searched for, the process marks itself as “completed” and immediately sends out a notification to all other processes of “completion.” Subsequently all other processes receive this notification and mark themselves as “completed”. `completed` here is a Boolean private to each process which ceases the execution of the process. When `BFS.dis` is run, you can see special output made by the processes when it reaches the completion stage.

The other alternate termination state is that, the element was not found in the graph. When this happens it is not as easy for each process to know that the graph has been completely pruned since they’re all working on separate chunks of the graph. The algorithm handles this problem by using a set variable called “unserviced” private to each process. Anytime a process receives a request for work from another process and is unable to service it, it adds that process to this set. When the case of element not being found occurs, every process begins to starve – since all of their work queues run dry. When this happens, the size of the “unserviced” set slowly builds up. The same DistAlgo `await` condition that waits for work or completion, also checks if the number of unserviced processes = the number of other processes. When this condition is satisfied it knows that the search was unsuccessful and the element is not in the graph.

Testing & Caveats
-----------------
When run, each node prints a message for each node it inspects. It also prints messages when it requests work from another process, receives a request for work, gets work, etc.

The following a few sample test runs of the algorithm:

#### Sample Test Run

	arjun@arjun-desktop:~/dev/workspace/Distributed-Graph-Algorithms/Breadth-First-Search$ ./run.py
	The nodes in the graph and their randomly chosen attributes are: 
	1  --->  18
	2  --->  23
	3  --->  1
	4  --->  46
	5  --->  43
	6  --->  28
	Pick the attribute/value you would like to search for: 23

	[2012-10-18 06:12:03,977]runtime:INFO: Creating instances of P..
	[2012-10-18 06:12:03,982]runtime:INFO: 4 instances of P created.
	[2012-10-18 06:12:03,988]runtime:INFO: Starting procs...
	[2012-10-18 06:12:03,989]P(2):INFO: Empty queue; sending requests for work
	[2012-10-18 06:12:03,989]P(3):INFO: Empty queue; sending requests for work
	[2012-10-18 06:12:03,989]P(0):INFO: Empty queue; sending requests for work
	[2012-10-18 06:12:03,989]P(1):INFO: Inspected 1
	[2012-10-18 06:12:03,990]P(1):INFO: Received request for work from 2
	[2012-10-18 06:12:03,991]P(1):INFO: Giving work [2] to 2
	[2012-10-18 06:12:03,991]P(2):INFO: Received request for work from 3
	[2012-10-18 06:12:03,992]P(3):INFO: Received request for work from 2
	[2012-10-18 06:12:03,993]P(1):INFO: Received request for work from 3
	[2012-10-18 06:12:03,993]P(2):INFO: Received request for work from 0
	[2012-10-18 06:12:03,993]P(1):INFO: Received request for work from 0
	[2012-10-18 06:12:03,993]P(3):INFO: Received request for work from 0
	[2012-10-18 06:12:03,994]P(1):INFO: Inspected 6
	[2012-10-18 06:12:03,994]P(2):INFO: Got work [2] from 1
	[2012-10-18 06:12:03,994]P(1):INFO: Inspected 2
	[2012-10-18 06:12:03,994]P(0):INFO: Received request for work from 2
	[2012-10-18 06:12:03,995]P(1):INFO: Value 23 found. BFS Completed!!!
	[2012-10-18 06:12:03,995]P(2):INFO: Inspected 2
	[2012-10-18 06:12:03,995]P(0):INFO: Received request for work from 3
	[2012-10-18 06:12:03,995]P(2):INFO: Value 23 found. BFS Completed!!!
	[2012-10-18 06:12:03,996]P(3):INFO: Received notice that 2 found value 23. Terminating!
	[2012-10-18 06:12:03,996]P(0):INFO: Received notice that 2 found value 23. Terminating!
	[2012-10-18 06:12:04,003]runtime:INFO: ***** Statistics *****
	* Total procs: 4

In this run, the value `23` was found by process number `2`.

#### Sample Test Run

	arjun@arjun-desktop:~/dev/workspace/Distributed-Graph-Algorithms/Breadth-First-Search$ ./run.py
	The nodes in the graph and their randomly chosen attributes are: 
	1  --->  29
	2  --->  8
	3  --->  30
	4  --->  17
	5  --->  23
	6  --->  39
	Pick the attribute/value you would like to search for: 39

	[2012-10-18 06:10:31,864]runtime:INFO: Creating instances of P..
	[2012-10-18 06:10:31,869]runtime:INFO: 4 instances of P created.
	[2012-10-18 06:10:31,876]runtime:INFO: Starting procs...
	[2012-10-18 06:10:31,877]P(0):INFO: Empty queue; sending requests for work
	[2012-10-18 06:10:31,877]P(2):INFO: Empty queue; sending requests for work
	[2012-10-18 06:10:31,877]P(1):INFO: Inspected 1
	[2012-10-18 06:10:31,877]P(3):INFO: Empty queue; sending requests for work
	[2012-10-18 06:10:31,877]P(1):INFO: Inspected 2
	[2012-10-18 06:10:31,878]P(1):INFO: Inspected 3
	[2012-10-18 06:10:31,879]P(1):INFO: Inspected 4
	[2012-10-18 06:10:31,879]P(1):INFO: Received request for work from 0
	[2012-10-18 06:10:31,880]P(2):INFO: Received request for work from 3
	[2012-10-18 06:10:31,880]P(2):INFO: Received request for work from 0
	[2012-10-18 06:10:31,880]P(1):INFO: Giving work [4] to 0
	[2012-10-18 06:10:31,880]P(3):INFO: Received request for work from 2
	[2012-10-18 06:10:31,880]P(0):INFO: Received request for work from 2
	[2012-10-18 06:10:31,880]P(3):INFO: Received request for work from 0
	[2012-10-18 06:10:31,881]P(0):INFO: Received request for work from 3
	[2012-10-18 06:10:31,881]P(1):INFO: Received request for work from 2
	[2012-10-18 06:10:31,881]P(1):INFO: Giving work [5] to 2
	[2012-10-18 06:10:31,882]P(0):INFO: Got work [4] from 1
	[2012-10-18 06:10:31,882]P(0):INFO: Inspected 4
	[2012-10-18 06:10:31,883]P(2):INFO: Got work [5] from 1
	[2012-10-18 06:10:31,882]P(1):INFO: Received request for work from 3
	[2012-10-18 06:10:31,882]P(0):INFO: Inspected 5
	[2012-10-18 06:10:31,883]P(2):INFO: Inspected 5
	[2012-10-18 06:10:31,883]P(2):INFO: Empty queue; sending requests for work
	[2012-10-18 06:10:31,883]P(1):INFO: Giving work [6] to 3
	[2012-10-18 06:10:31,883]P(0):INFO: Inspected 6
	[2012-10-18 06:10:31,883]P(0):INFO: Value 39 found. BFS Completed!!!
	[2012-10-18 06:10:31,884]P(3):INFO: Received request for work from 2
	[2012-10-18 06:10:31,884]P(1):INFO: Inspected 5
	[2012-10-18 06:10:31,885]P(2):INFO: Received notice that 0 found value 39. Terminating!
	[2012-10-18 06:10:31,885]P(1):INFO: Received request for work from 2
	[2012-10-18 06:10:31,885]P(3):INFO: Got work [6] from 1
	[2012-10-18 06:10:31,885]P(1):INFO: Giving work [6] to 2
	[2012-10-18 06:10:31,885]P(3):INFO: Received notice that 0 found value 39. Terminating!
	[2012-10-18 06:10:31,886]P(1):INFO: Received notice that 0 found value 39. Terminating!
	[2012-10-18 06:10:31,886]P(1):INFO: Inspected 5
	[2012-10-18 06:10:31,891]runtime:INFO: ***** Statistics *****
	* Total procs: 4

In this run, the value `39` was found by process number `0`.

#### Sample Test Run

	arjun@arjun-desktop:~/dev/workspace/Distributed-Graph-Algorithms/Breadth-First-Search$ ./run.py
	The nodes in the graph and their randomly chosen attributes are: 
	1  --->  30
	2  --->  27
	3  --->  46
	4  --->  5
	5  --->  50
	6  --->  37
	Pick the attribute/value you would like to search for: 3545

	[2012-10-18 06:13:24,051]runtime:INFO: Creating instances of P..
	[2012-10-18 06:13:24,056]runtime:INFO: 4 instances of P created.
	[2012-10-18 06:13:24,064]runtime:INFO: Starting procs...
	[2012-10-18 06:13:24,065]P(2):INFO: Empty queue; sending requests for work
	[2012-10-18 06:13:24,065]P(0):INFO: Empty queue; sending requests for work
	[2012-10-18 06:13:24,065]P(3):INFO: Empty queue; sending requests for work
	[2012-10-18 06:13:24,065]P(1):INFO: Inspected 1
	[2012-10-18 06:13:24,066]P(1):INFO: Inspected 2
	[2012-10-18 06:13:24,066]P(1):INFO: Inspected 4
	[2012-10-18 06:13:24,066]P(1):INFO: Inspected 5
	[2012-10-18 06:13:24,067]P(1):INFO: Inspected 6
	[2012-10-18 06:13:24,068]P(1):INFO: Received request for work from 3
	[2012-10-18 06:13:24,068]P(2):INFO: Received request for work from 3
	[2012-10-18 06:13:24,068]P(0):INFO: Received request for work from 2
	[2012-10-18 06:13:24,068]P(3):INFO: Received request for work from 2
	[2012-10-18 06:13:24,068]P(3):INFO: Received request for work from 0
	[2012-10-18 06:13:24,068]P(2):INFO: Received request for work from 0
	[2012-10-18 06:13:24,069]P(1):INFO: Giving work [4] to 3
	[2012-10-18 06:13:24,070]P(0):INFO: Received request for work from 3
	[2012-10-18 06:13:24,070]P(3):INFO: Got work [4] from 1
	[2012-10-18 06:13:24,070]P(1):INFO: Received request for work from 0
	[2012-10-18 06:13:24,070]P(1):INFO: Giving work [6] to 0
	[2012-10-18 06:13:24,070]P(3):INFO: Inspected 4
	[2012-10-18 06:13:24,071]P(3):INFO: Inspected 3
	[2012-10-18 06:13:24,071]P(3):INFO: Empty queue; sending requests for work
	[2012-10-18 06:13:24,071]P(1):INFO: Received request for work from 2
	[2012-10-18 06:13:24,071]P(0):INFO: Got work [6] from 1
	[2012-10-18 06:13:24,072]P(1):INFO: Giving work [3] to 2
	[2012-10-18 06:13:24,072]P(0):INFO: Inspected 6
	[2012-10-18 06:13:24,072]P(2):INFO: Received request for work from 3
	[2012-10-18 06:13:24,072]P(1):INFO: Inspected 5
	[2012-10-18 06:13:24,073]P(1):INFO: Received request for work from 3
	[2012-10-18 06:13:24,073]P(1):INFO: Giving work [6] to 3
	[2012-10-18 06:13:24,073]P(1):INFO: Inspected 3
	[2012-10-18 06:13:24,073]P(1):INFO: Empty queue; sending requests for work
	[2012-10-18 06:13:24,073]P(2):INFO: Got work [3] from 1
	[2012-10-18 06:13:24,073]P(0):INFO: Received request for work from 3
	[2012-10-18 06:13:24,073]P(3):INFO: Got work [6] from 1
	[2012-10-18 06:13:24,074]P(2):INFO: Inspected 3
	[2012-10-18 06:13:24,074]P(0):INFO: Received request for work from 1
	[2012-10-18 06:13:24,074]P(0):INFO: Inspected 3
	[2012-10-18 06:13:24,074]P(3):INFO: Received request for work from 1
	[2012-10-18 06:13:24,074]P(0):INFO: Empty queue; sending requests for work
	[2012-10-18 06:13:24,074]P(2):INFO: Received request for work from 1
	[2012-10-18 06:13:24,075]P(3):INFO: Inspected 6
	[2012-10-18 06:13:24,075]P(2):INFO: Empty queue; sending requests for work
	[2012-10-18 06:13:24,075]P(0):INFO: Unable to get work. Assuming value 3545 not in the graph. Terminating... 
	[2012-10-18 06:13:24,075]P(1):INFO: Received request for work from 0
	[2012-10-18 06:13:24,075]P(3):INFO: Received request for work from 0
	[2012-10-18 06:13:24,076]P(3):INFO: Empty queue; sending requests for work
	[2012-10-18 06:13:24,076]P(2):INFO: Unable to get work. Assuming value 3545 not in the graph. Terminating... 
	[2012-10-18 06:13:24,076]P(1):INFO: Received request for work from 2
	[2012-10-18 06:13:24,077]P(3):INFO: Unable to get work. Assuming value 3545 not in the graph. Terminating... 
	[2012-10-18 06:13:24,077]P(1):INFO: Received request for work from 3
	[2012-10-18 06:13:24,078]P(1):INFO: Unable to get work. Assuming value 3545 not in the graph. Terminating... 
	[2012-10-18 06:13:24,081]runtime:INFO: ***** Statistics *****
	* Total procs: 4

	[2012-10-18 06:13:24,083]runtime:INFO: Terminating...


In this test run, we look out for the non-existent value `3545`. As each process is work-starved, it terminates itself. The result (shown above) means that a node with that value does not exist in the graph.

### Longer Sample Test Run

The file `test_run_10_100_200.txt` contains the output of running `./run.py -w 10 -n 100 -e 200`. It's much longer (and therefore more interesting) than the previous ones.

### Caveats

Overall, with medium-sized graphs (about a thousands nodes); this BFS algorithm works fine and does what it’s supposed to do. However when handling large graph sizes, it may or may not run into problems. This is because currently DistAlgo has a limit on how large the size of a message send between processes can be. The way the algorithm is implemented; in response to a work request, it sends a list of all nodes it has visited so far. This is to avoid re-visiting already inspected nodes, and to _effectively_ turn the graph into a tree. The algorithm does not take packet loss into consideration, so when it occurs the behavior of the algorithm is undefined.

---
