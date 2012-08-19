
import sys
sys.path.append("..") # in order to import NetworkX

import networkx as nx
from collections import deque

nprocs = 4 # default
tree = nx.balanced_tree(4, 4)
element_to_search_for = 300

procs = dict() # dict mapping process numbers to processes
Pi = lambda p: int(str(p))

class P(DistProcess):
    
    def setup(ps):
        other_procs = ps
        q = deque()
        inspected = set()
        
        if Pi(self) == 0:
            q.appendleft(0)
        
        completed = False
        unserviced = set()

    def cs(search_for):
        # todo: what if search_for can't be found?
        --start
        if len(q) > 0:
            '''Pop one node, check if it's what we're searching for'''
            inspect = q.pop()
            inspected.update({inspect})
            output("Inspected "+str(inspect))
            
            if search_for == inspect:
                completed = True
                output("Element %r found. BFS Completed!!!" % search_for)
                
                '''Send messages to all processes notifying them of the completion'''
                send(Reply("completed"), other_procs)
                
                return
            
            else:
                '''Fill work queue with un-inspected child nodes'''
                children = set( tree[inspect] ) - inspected
                
                for child in children:
                    #tree.node[child]['parent'] = inspect
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
                output("Unable to get work. Assuming element %d not in tree. Terminating... " % 
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
            #unserviceable_requests += 1
            #output("Could not service %r. Total waiting: %d" % (_source, unserviceable_requests))

    def OnReply(m):
        if m == "completed":
            completed = True
            output("Received notice that %r found elem %d. Terminating!" % 
                   (_source, element_to_search_for))
        elif isinstance(m, tuple):
            item, _inspected = m
            output('Got work [' + repr(item) + "] from " + str(_source))
            inspected.update(_inspected)
            q.appendleft(item)
            #unserviceable_requests = 0

    def main():
        while not completed:
            cs(element_to_search_for)

def main():
    global tree, element_to_search_for
    
    # configuration: number of processes
    global nprocs
    if len(sys.argv) > 1:
        nprocs = int(sys.argv[1])
    
    # configuration: element_to_search_for    
    if len(sys.argv) > 2:
        element_to_search_for = int(sys.argv[2])
    
    # configuration: tree
    if len(sys.argv) > 4:
        r, d = int(sys.argv[3]), int(sys.argv[4])
        print("Replacing default (r=4,depth=4) tree with new tree of (r = %d, depth = %d)..." % (r, d))
        tree = nx.balanced_tree(r, d)
    
    nx.freeze(tree)
    print("Searching for the element %d using BFS in a tree containing %d nodes." % 
        ( element_to_search_for, len(tree.nodes())) )
    
    # create n process
    use_channel("tcp")
    ps = createprocs(P, {str(i) for i in range(0, nprocs)})
    global procs
    for (pn, p) in ps.items():
        procs[int(pn)] = p
    ps = set(ps.values())

    # setup the processes
    for p in ps: setupprocs([p], [ps-{p}])

    startprocs(ps)

    for p in (ps): p.join()
    
