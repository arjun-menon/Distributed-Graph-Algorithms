#!/usr/bin/python3

#
# Kruskal's algorithm for sequentially finding 
# theMinimum Spanning Tree (MST) of a graph.
#

import sys
sys.path.append('..')
import networkx as nx

def construct_graph(numbered=False):

    if numbered:
        A, B, C, D, E, F, G, H, I, J = [str(i) for i in range(1,11)]
    else:    
        A, B, C, D, E, F, G, H, I, J = 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'
    
    def edge(n1, n2, w):
        return (n1, n2, {'weight':w})
    
    edge_list = [
    edge(A,F,2),
    edge(F,G,7),
    edge(G,H,15 ),
    edge(H,J,13),
    edge(J,I,9),
    edge(I,C,18),
    edge(C,B,17),
    edge(B,A,3),
    
    edge(E,F,1),
    edge(E,G,6),
    edge(E,H,5),
    edge(E,I,10),
    edge(E,D,11),
    
    edge(I,H,12),
    edge(D,I,4),
    edge(D,C,8),
    edge(D,B,16)]
    
    G = nx.Graph()
    G.add_edges_from(edge_list)
    
    #for e in G.edges(data=True):
    #    print(e)
    return G


def kruskal(G):
    """
    Implementation of _sequential_ Kruskal's algorithm based on Wikipedia description:
    -----------------------------------------------------------------------------------
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


def verify_solution(G, sol):
    '''Verify the solution for MST against NetworkX's built-in MST solver.
       Only works if the solution is unique (=> edges have unique weights.)'''
    
    nx_sol = set( nx.minimum_spanning_tree(G).edges() )
    
    return nx_sol == sol


def draw_graph_using_matplotlib(highlighted_edges, show = False):
    import matplotlib
    if matplotlib.rcParams['backend'] == 'agg':
        matplotlib.rcParams['backend'] = "Qt4Agg"
    
    import matplotlib.pyplot as plt
    
    pos=nx.spring_layout(G, weight = None)
    nx.draw_networkx_nodes(G,pos, node_size=330)
    nx.draw_networkx_edges(G,pos, set(G.edges()) - set(highlighted_edges), width=2)
    nx.draw_networkx_edges(G,pos, highlighted_edges, width=3, edge_color='blue')
    nx.draw_networkx_labels(G,pos, font_size=12, font_family='sans-serif')

    plt.draw()
    
    if show:
        plt.show()

def render_solution(sol):
    edge_list = ["(%s, %s)" % (min(edge), max(edge)) for edge in sol]
    edge_list.sort()
    return ", ".join(edge_list)

if __name__ == "__main__":
    visualize = False
    if len(sys.argv) > 1 and sys.argv[1] == '-v':
        visualize = True
    else:
        print("To visualize the graph and its solution using matplotlib, use the optarg -v")

    G = construct_graph(numbered=False)
    
    sol = kruskal(G)
    
    if not verify_solution(G, sol):
        raise Exception("Solution to MST is incorrect")
    
    print("Solution:", render_solution(sol))
    
    if visualize:
        draw_graph_using_matplotlib(sol, show=True)
