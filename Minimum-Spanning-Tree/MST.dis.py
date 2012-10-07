
'''
Distributed Minimum Spanning Tree (MST) Solver in DistAlgo.
Based on the Gallager, Humblet and Spira algorithm for distributed MST.
'''

# Note:
# This program cannot be run directly using Python.
# You can use the `run.py` file instead to run this program.
# Alternatively you can use the symlink pointing to this file, 
# with the extension `.dis` and run it directly with DistAlgo.
# The .py extnesion was appended to activate Python syntax
# highlighting in various editors, GitHub, etc.

from collections import deque
from tools import *

sys.argv = sys.argv[1:]
tools = Tools()

class Spark(DistProcess):
    def setup(ps):
        ps = ps
        finished = False
        branches = set()
        query_reply_count = None

    def OnFinished():
        finished = True

    def OnBranches(bset):
        branches.update(bset)
        query_reply_count -= 1

    def main():
        # for p in ps:
        #     send( Wakeup(), p )        
        random_node =  ps.pop()
        ps.update( {random_node} )
        send( Wakeup(), random_node )

        await(finished)

        query_reply_count = 0
        for p in ps:
            send( QueryBranches(), p )
            query_reply_count += 1

        await(query_reply_count == 0)

        for p in ps:
            send( Finished(), p )

        output("Solution: %s" % tools.repr_solution(branches))
        tools.present_solution(branches)


INFINITY = 999999999

class ConnectRequests(object):
    def __init__():
        self.reqs = dict()

    def insert(p, l):
        if p in self.reqs:
            print("ERROR: %r already made a request" % p)
        else:
            self.reqs[p] = l

    def get_least_level_req():
        if self.reqs:
            return min(self.reqs, key=self.reqs.get)

    def least_level():
        if self.reqs:
            return self.reqs[self.get_least_level_req()]
        else:
            return INFINITY

# Used by the SE variable in Node:
BASIC = 'Basic'
BRANCH = 'Branch'
REJECTED = 'Rejected'

# Used by the my_state variable in Node:
SLEEPING = "Sleeping"
FOUND = 'Found'
FIND = 'Find'

class Node(DistProcess):
    def setup(edges, spark):
        spark = spark

        w = edges
        neighbors = set( edges.keys() )

        # State of each Edge/node:
        SE = dict()
        for n in neighbors:
            SE[n] = BASIC

        # Level & State of this Node:
        my_level = 0
        my_fragm = None
        my_state = SLEEPING

        # misc:
        expect_core_report = None
        report_over = False
        other_core_node = None
        discovery = None

        waiting_to_connect_to = None
        connect_reqs = ConnectRequests()
        find_count = None # hmmm
        find_source = None
        test_reqs = set()
        min_wt_outgoing = (None, INFINITY)

        # Used by the Test functions:
        best_wt = INFINITY
        best_path = None
        test_over = None

        # Special variable to indicate when to terminate:
        finished = False

    def OnQueryBranches():
        branches = set()

        for node in {edge for edge, state in SE.items() if state == BRANCH}:
            edge_nodes = [str(self), str(node)]
            edge_str = ( str( min(edge_nodes) ), str( max(edge_nodes) ) )
            branches.update( { edge_str } )

        send( Branches(branches), spark )

    def OnFinished():
        finished = True

    def OnWakeup():
        output("Received spontaneous Wakeup from: %r" % _source)
        wakeup_if_necessary()

    def wakeup_if_necessary():
        if my_state == SLEEPING:
            output("%r is waking up!" % self)
            # todo: call a function that finds min-wt BASIC node instead..
            # adjacent edge/node of minimum weight:
            m = min(edges, key=edges.get)
            my_state = FOUND

            send( Connect(my_level), m )
            SE[m] = BRANCH
            waiting_to_connect_to = m

    def OnConnect(L):
        j = _source
        output("Received Connect(%r) from: %r" % (L, j))

        wakeup_if_necessary()
        connect_reqs.insert(j, L)

    def OnTest(L, F):
        j = _source
        output("Received Test(%r, %r) from: %r" % (L, F, j))

        wakeup_if_necessary()
        test_reqs.update({ (L, F, j) })

    def OnInitiate(L, F, S, merge):
        j = _source
        output("Received Initiate(%r, %r, %r) from: %r" % (L, F, S, j))

        my_level = L
        my_fragm = F
        my_state = S

        best_wt = INFINITY
        best_path = None

        if merge == True:
            other_core_node = j
        else:
            other_core_node = None

        SE[j] = BRANCH

        my_branches = {edge for edge, state in SE.items() if state == BRANCH}
        my_branches -= {_source}

        find_count = 0
        for b in my_branches:
            send( Initiate(my_level, my_fragm, my_state, False), b )
            if my_state == FIND:
                find_count += 1
                output("%r has sent FIND to branch %r" % (self, b))

        if my_state == FIND:
            find_source = j
            report_over = False
            test()

    def merge_with(node):
        output("%r merging with %r" % (self, node))

        new_level = my_level + 1
        new_fragm = w[node]

        # Edge marked as branch. It has not been sent an Initiate yet though:
        SE[node] = BRANCH

        send( Initiate(new_level, new_fragm, FIND, True), node )
        expect_core_report = True
        discovery = False

    def absorb_node(node):
        output("%r absorbing %r" % (self, node))

        send( Initiate(my_level, my_fragm, my_state, False), node )
        SE[node] = BRANCH

        if my_state == FIND:
            find_count += 1
            output("%r has sent FIND to branch %r" % (self, node))

    def test():
        # Edges in the state BASIC:
        basic_edges = [edge for edge, state in SE.items() if state == BASIC]

        # test_over is used to notify the await condition that the testing is over
        test_over = False

        if basic_edges:
            # find the minimum-weight adjacent edge in state BASIC:
            test_edge = min(basic_edges, key = lambda edge: w[edge])

            send( Test(my_level, my_fragm), test_edge )
            output("%r has sent Test() to %r" % (self, test_edge))
        else:
            # There are no BASIC edges.
            test_over = True

    def test_reply_condition():
        # Condition (3) [pg. 8 of the enhanced GHS paper]
        # If the id in the message differs from the id of the fragment the node 
        # belongs to and the level in the message is higher than that of the 
        # node's fragment – no reply is sent until the situation has changed. 
        return bool( { True for (L, F, j) in test_reqs if F == my_fragm 
            or (F!=my_fragm and L <= my_level) } )

    def test_reqs_process():
        to_remove = set()

        for (L, F, j) in test_reqs:
            # Condition (1)
            # If the id in the message is the same as the id of the fragment the 
            # node belongs to – a reject message is sent back
            if F == my_fragm:
                send( Reject(), j )
                output("%r sent Reject() to %r" % (self, j))
                to_remove.update({ (L, F, j) })

            # Condition (2)
            # If the id in the message differs from the id of the fragment the node 
            # belongs to and the level in the message is lower or equal to that of 
            # the node's fragment – an accept message is sent back.
            elif L <= my_level: # F != my_fragm is implied
                send( Accept(), j )
                output("%r sent Accept() to %r" % (self, j))
                to_remove.update({ (L, F, j) })

        test_reqs -= to_remove

    def OnReject(): # reply to Test
        j = _source
        output("%r Received Reject() from: %r" % (self, j))

        if SE[j] == BASIC:
            SE[j] = REJECTED

        test()

    def best_path_repr():
        if best_path:
            return " -> ".join(str(node) for node in best_path)
        else:
            return "No Outgoing edges"

    def OnAccept(): # reply to Test
        j = _source

        if w[j] < best_wt:
            best_path = [self, j]
            best_wt = w[j]

        output("Outgoing Neighbor %s @ %d [find_count = %d]" % (best_path_repr(), best_wt, find_count))
        test_over = True

    def report():
        # Reset test_over, so that report_conition doesn't become true again
        test_over = None

        my_state = FOUND
        output("Least weight(%d) outgoing edge from %r: %s" % (best_wt, self, best_path_repr()))

        send(Report(best_wt, best_path), find_source)
        report_over = True

    def OnReport(w, path):
        if _source == other_core_node:
            expect_core_report = False
            output("Received %s @ %d from other core node %r" % (path, w, _source))
        else:
            if find_count > 0:
                find_count -= 1
                output("Received %s @ %d from %r [find_count = %d]" % (path, w, _source, find_count))
            else:
                output("ERROR: Received non-core Report(%r, %r) from %r when find_count is %r" % (w, path, _source, find_count))

        if w < best_wt:
            best_path = [self] + path
            best_wt = w

    def OnFragConn(path):
        if my_state != FOUND:
            output("ERROR")

        if len(path) == 1:
            node = path[0]
            output("Fragment (%d) ------------ Sending Connect(%d) to %r" % (my_fragm, my_level, node))

            send( Connect(my_level), node )
            SE[node] = BRANCH
            waiting_to_connect_to = node

        elif len(path) > 1:
            hd = path[0]
            tl = path[1:]
            send(FragConn(tl), hd)

    def init_fragment_connect():
        """The fragment sends a Connect() over the minimum-weight outgoing edge."""
        discovery = True
        expect_core_report = None
        report_over = False # necessary ?

        if not best_path:
            output("----- NO MORE OUTGOING EDGES -----")
            send( Finished(), spark )

        elif best_path[1] != other_core_node:
            output("Least weight(%d) outgoing edge of fragment(%d): %s !!!!!!!!!!!!!!!"
                    % (best_wt, my_fragm, best_path_repr()))
            
            hd = best_path[0]
            tl = best_path[1:]
            send(FragConn(tl), hd)

    def main():
        while not finished:

            absorb_condition = lambda: connect_reqs.least_level() < my_level
            merge_condition = lambda: waiting_to_connect_to in set(connect_reqs.reqs)
            report_condition = lambda: test_over and find_count == 0 # must be 0, not None
            fragment_connect_condition = lambda: expect_core_report == False and report_over and discovery == False

            await(  merge_condition() or absorb_condition() or test_reply_condition() 
                or report_condition() or fragment_connect_condition() or finished  )

            if merge_condition():
                merge_with(waiting_to_connect_to)
                connect_reqs.reqs.pop(waiting_to_connect_to)
                waiting_to_connect_to = None

            elif absorb_condition():
                node = connect_reqs.get_least_level_req()
                absorb_node(node)
                connect_reqs.reqs.pop(node)

            elif test_reply_condition():
                test_reqs_process()

            elif report_condition():
                report()

            elif fragment_connect_condition():
                init_fragment_connect()

def main():
    G = tools.graph

    # Create the processes
    # --------------------
    use_channel("tcp")

    nodes = createprocs(Node, set(G.nodes()))
    node_ps = set(nodes.values())

    spark = createprocs(Spark, set(['Spark']))
    spark_p = spark['Spark']

    # Setup the processes
    # -------------------
    for p in node_ps:
        edges = { nodes[node] : data['weight'] for (node, data) in G[repr(p)].items() }
        setupprocs([p], [edges, spark_p])

    setupprocs([spark_p], [node_ps])

    # Start the processes
    # -------------------
    startprocs(node_ps)
    startprocs([spark_p])

    # Wait for the processes to die
    # -----------------------------
    for p in node_ps:
        p.join()
    
    spark_p.join()
