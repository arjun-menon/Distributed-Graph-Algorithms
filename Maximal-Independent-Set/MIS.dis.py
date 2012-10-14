
'''
Distributed Maximal Independent Set (MST) Solver in DistAlgo.
'''

# Note:
# This program cannot be run directly using Python.
# You can use the `run.py` file instead to run this program.
# Alternatively you can use the symlink pointing to this file, 
# with the extension `.dis` and run it directly with DistAlgo.
# The .py extnesion was appended to activate Python syntax
# highlighting in various editors, GitHub, etc.

import random
from InputGraph import get_graph

G = get_graph()

class P(DistProcess):
    def setup(ps, edges):
        if str(self) == '0':
            other_procs = ps
            vertices = set()
        else:
            control_proc = ps
            edges = edges

        # Possible states a node could be in:
        NORMAL = 'NORMAL' # Initial state of all nodes
        VERTEX = 'VERTEX' # Indicates that the node is part of the MIS
        OUT = 'OUT' # Nieghbor nodes marked as not being a part of the MIS

        # Used for marking
        out_confirmations = set()
        state = NORMAL

        # Used for search:
        search_requested = set()
        search_reply_count = 0
        collected_replies = set()

        # Used for control purposes:
        call = 'none'
        call_args = None

        done = False

    ####################
    # Search Functions #
    ####################

    def search(path, source):
        #output("search(%r, %r)..." % (path, source))

        collected_replies = []
        if state == NORMAL:
            collected_replies.append(path)

        neighbors = set( edges.keys() ) - set(path)

        search_reply_count = 0
        for neighbor in neighbors:
            send(Search(path+[neighbor]), neighbor)

        await( search_reply_count == len(neighbors) )

        #output("%r ---- %r" % (self, collected_replies))
        if source:
            send(SearchReply(collected_replies), source)
        else:
            return collected_replies

    def OnSearchReply(paths):
        search_reply_count += 1
        if paths:
            collected_replies += paths

    def OnSearch(path):
        root = path[0]

        if root in search_requested:
            send(SearchReply(None), _source)

        else:
            search_requested.update( {root} )

            call_args = (path, _source)
            call = 'search'

    ##########################
    # Node Marking Functions #
    ##########################

    def setState(new_state):
        if new_state != state:
            state = new_state
            output("%r marked as %s" % (self, state))

    def OnMark(path):
        if not path:
            call = 'mark'
        else:
            next, path = path[0], path[1:]
            send(Mark(path), next)

    def mark():
        '''Node marks itself as a VERTEX and signals
           neighbors to mark themselves as OUT '''

        setState(VERTEX)
        send(Marked(), control_proc)

        neighbors = set(edges.keys())
        out_confirmations = set()

        for neighbor in neighbors:
            send(Out(), neighbor)

        await(out_confirmations == neighbors)
        #output("Out Confirmed: %r" % out_confirmations)

        search_source = None
        search_result = search([self], None)
        #output(search_result)

        if search_result:
            random_path = random.choice(search_result)
            random_path = random_path[1:]
            send(Mark(random_path[1:]), random_path[0])
        else:
            #output("Sending control proc message FINISHED...")
            send(Finished(), control_proc)
    
    def OnOut():
        setState(OUT)
        send(OutConfirmation(), _source)

    def OnOutConfirmation():
        out_confirmations.update({_source})

    #####################
    # Control Functions #
    #####################

    def node():
        while call and not done:
            # Using a copy of call
            _call = str(call)
            call = None

            if _call == 'none':
                pass
            elif _call == 'mark':
                mark()
            elif _call == 'search':
                search(*call_args)

            await(done or call)

        #output("Node %r is going DOWN..." % self)

    def OnDone():
        done = True
    
    def OnFinished():
        pass

    def OnMarked():
        vertices.update(str(_source))

    def controlProc():
        random_node = ps.pop()
        ps.add(random_node)

        send(Mark([]), random_node)
        await(received(Finished()))

        send(Done(), other_procs)
        output("Vertices in the MIS are: %s" % ", ".join(str(v) for v in vertices))
    
    def main():
        if str(self) == '0':
            controlProc()
        else:
            node()

def main():
    use_channel("tcp")
    
    procs_names = set(G.nodes())
    procs_names.update({'0'})# control process
    
    global procs
    procs = createprocs(P, procs_names)
    
    # setup the processes
    ps = set(procs.values())
    
    for p in ps:
        if str(p) == '0':
            setupprocs([p], [ps-{p}, None])
        else:
            p_edges = { procs[node] : data['weight'] 
                       for (node, data) in G[repr(p)].items() }
            #setupprocs([p], [ps-{p, procs['0']}, p_edges])
            setupprocs([p], [procs['0'], p_edges])
    
    startprocs(ps)
    
    for p in (ps):
        p.join()
