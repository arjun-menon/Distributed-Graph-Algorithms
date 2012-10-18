''''
Distributed processes-as-workers breadth-first search.
'''

import sys
sys.path.append("..") # in order to import NetworkX

import networkx as nx
from collections import deque

procs = dict() # dict mapping process numbers to processes
Pi = lambda p: int(str(p))

class P(DistProcess):
    
    def setup(ps, graph, element_to_search_for, starter):
        other_procs = ps
        graph = graph
        element_to_search_for = element_to_search_for

        q = deque()
        inspected = set()
        
        if starter:
            first_node = graph.nodes()[0]
            q.appendleft(first_node)
        
        completed = False
        unserviced = set()

    def search(search_for):
        --start
        if len(q) > 0:
            '''Pop one node, check if it's what we're searching for'''
            inspect = q.pop()
            inspected.update({inspect})
            output("Inspected "+str(inspect))
            
            if search_for == graph.node[inspect]['value']:
                completed = True
                output("Value %r found. BFS Completed!!!" % search_for)
                
                '''Send messages to all processes notifying them of the completion'''
                send(Reply("completed"), other_procs)
                
                return
            
            else:
                '''Fill work queue with un-inspected child nodes'''
                children = set( graph[inspect] ) - inspected
                
                for child in children:
                    q.appendleft(child)
        
        else:
            '''Send requests to other processes for work'''
            output("Empty queue; sending requests for work")
            send(Request( None ), other_procs)
            
            '''Await until work is received or BFS is completed'''
            await( len(q) > 0 or completed == True or ( len(unserviced) == len(other_procs) ) )
            
            if completed:
                return
            
            if ( len(unserviced) == len(other_procs) ):
                completed = True
                output("Unable to get work. Assuming value %d not in the graph. Terminating... " % 
                       element_to_search_for)
                return
        
        if len(q) > 1:
            '''Service requests for work if I have 2 or more nodes in my queue'''
            --reply
        
        --release
        --end

    def OnRequest(ts):
        output("Received request for work from " + str(_source))
        
        if len(q) > 1:
            '''Service request for work if I have 2 or more nodes in my queue'''
            
            work = (q.pop(), inspected)
            output('Giving work [' + repr(work[0]) + "] to " + str(_source))
            send(Reply(work), _source)
            unserviced.clear()
            
        else:
            unserviced.update({Pi(_source)})

    def OnReply(m):
        if m == "completed":
            completed = True
            output("Received notice that %r found value %d. Terminating!" % 
                   (_source, element_to_search_for))
        elif isinstance(m, tuple):
            item, _inspected = m
            output('Got work [' + repr(item) + "] from " + str(_source))
            inspected.update(_inspected)
            q.appendleft(item)

    def main():
        while not completed:
            search(element_to_search_for)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Perform breadth-first search on a random graph in paralell using several workers.')
    parser.add_argument('-w', '--workers', nargs=1, type=int, default=[4], help='Number of workers to do the search. [Default 4]')
    parser.add_argument('-n', '--nodes', nargs=1, type=int, default=[6], help='The maximum number of nodes in the random graph.')
    parser.add_argument('-e', '--edges', nargs=1, type=int, default=[10], help='The number of edges to form in the random graph.')
    args = parser.parse_args()
    nprocs = args.workers[0]
    n = args.nodes[0]
    e = args.edges[0]

    from graph_gen import networkx_random_weighted_graph
    graph = None

    repeat = True
    while repeat:
        print("Creating a random graph...")
        graph = networkx_random_weighted_graph(n, e)
        if nx.is_connected(graph):
            repeat = False
        else:
            print("Generated random graph was not a connected graph.")

    print("The nodes in the graph and their randomly chosen attributes are: ")
    for n in graph.nodes():
        print(n, ' ---> ', graph.node[n]['value'])

    element_to_search_for = int(input("Pick the attribute/value you would like to search for: "))
    print()
    
    # create n process
    use_channel("tcp")
    ps = createprocs(P, {str(i) for i in range(0, nprocs)})
    global procs
    for (pn, p) in ps.items():
        procs[int(pn)] = p
    ps = set(ps.values())

    # setup the processes
    starter = True
    for p in ps:
        setupprocs([p], [ps-{p}, graph, element_to_search_for, starter])
        starter = False

    startprocs(ps)
    for p in (ps): p.join()
