#!/usr/bin/python3

'''
Kruskal's algorithm for sequentially finding 
the Minimum Spanning Tree (MST) of a graph.
'''

from tools import *

def kruskal(G):
    """
    Implementation of _sequential_ Kruskal's algorithm based on the Wikipedia description:
    --------------------------------------------------------------------------------------
    create a forest F (a set of trees), where each vertex in the graph is a separate tree
    create a set S containing all the edges in the graph
    while S is nonempty and F is not yet spanning
        remove an edge with minimum weight from S
        if that edge connects two different trees, then add it to the forest, combining two trees into a single tree
        otherwise discard that edge.
    At the termination of the algorithm, the forest has only one component and forms a minimum spanning tree of the graph.
    """
    
    class Forest(object):
        
        class TreeInForest(object):
            def __init__(self, node):
                self.nodes = {node}
                self.edges = set()
            def __str__(self):
                return repr(self.nodes) + " | " + repr(self.edges)
        
        def __init__(self, nodes):
            self.forest = list()
            
            for node in nodes:
                self.forest.append( self.TreeInForest(node) )
        
        def attempt_merge(self, edge):
            e1, e2 = edge
            e1_t = None
            e2_t = None
            
            for t in self.forest:
                if e1 in t.nodes and e2 in t.nodes:
                    return False
                
                if e1 in t.nodes:
                    e1_t = t
                if e2 in t.nodes:
                    e2_t = t
            
            "Merge: "
            e1_t.nodes.update(e2_t.nodes)
            e1_t.edges.update({edge})
            e1_t.edges.update(e2_t.edges)
            
            self.forest.remove(e2_t)
            return True
        
        def isSpanning(self):
            return len(self.forest) == 1
        
        def __str__(self):
            return '\n' + '\n'.join(str(t) for t in self.forest)
        
        def solution(self):
            if self.isSpanning():
                return self.forest[0].edges
    
    forest = Forest(G.nodes())
    
    edges = set(G.edges())
    edge_weight = lambda edge: G[ edge[0] ][ edge[1] ]['weight']
    
    while len(edges) and not forest.isSpanning():
        min_wt_edge = min(edges, key=edge_weight)
        forest.attempt_merge(min_wt_edge)
        edges.remove(min_wt_edge)
    
    return forest.solution()

if __name__ == "__main__":
    tools = Tools()
    G = tools.graph

    sol = kruskal(G)
    
    if not tools.verify_solution(sol):
        raise Exception("Solution to MST is incorrect")
    
    print("Solution:", tools.repr_solution(sol))
    tools.present_solution(sol)
