
import sys
sys.path.append('..')
import networkx as nx

class Tools(object):
    """Helps with the distributed and sequential (Kruskal) solver.
Provides services like handling optargs, setting up the graph, solution verification, drawing, etc."""

    def __init__(self):
        "Process command-line arguments and build the graph."

        import argparse
        import matplotlib

        parser = argparse.ArgumentParser(description='Finds the Minimum Spanning Tree (MST) of a given graph.')
        parser.add_argument('graph', nargs='?', type=self.construct_graph, default='graph-2', help=
    'File listing the edges of a graph line-by-line in the following style: "A B 2", where "A" and "B" are node names and "2" is the weight of the edge connecting them.')

        parser.add_argument('-v', '--visualize', action='store_true', help=
    'Visualize the graph and its solution using matplotlib, with the branches of the MST marked in thick blue.')

        parser.add_argument('-b', '--backend', nargs=1, type=matplotlib.rcsetup.validate_backend, default=['Qt4Agg'], help=
    'Interactive GUI backend to be used by matplotlib for visualization. Potential options are: %s. Default value is Qt4Agg.' % ', '.join(matplotlib.rcsetup.interactive_bk))

        parser.add_argument('-o', '--output', nargs=1, type=argparse.FileType('w'), default=[open('sol', 'w')], help=
    'File to write the solution (MST edge list) to. By default it written to the file `sol`.')

        args = parser.parse_args()
        
        self.backend = args.backend[0]
        self.visualize = args.visualize
        self.output_file = args.output[0]
        self.graph = args.graph

    def construct_graph(self, file):
        seen_w = set()

        def edge(n1, n2, w):
            if w in seen_w:
                raise Exception("Duplicate edge weights in graph. For a unique MST, all edge weights have to be uniqe as well.")
            seen_w.update({ w })
            return (n1, n2, {'weight':w})

        edge_list = list()

        with open(file, 'r') as f:
            edge_list = list( edge(ed.split()[0], ed.split()[1], int(ed.split()[2])) 
                for ed in 
                (e.strip() for e in f.readlines() if e.strip() != "") 
                if len(ed.split()) == 3 )

            G = nx.Graph()
            G.add_edges_from(edge_list)

            self.graph = G
            return G

    def verify_solution(self, sol):
        '''Verify the solution for MST against NetworkX's built-in MST solver.
           Only works if the solution is unique (=> edges have unique weights.)'''
        
        nx_sol = set( nx.minimum_spanning_tree(self.graph).edges() )
        
        return nx_sol == sol

    def repr_solution(self, sol):   
        edge_list = ["(%s, %s)" % (min(edge), max(edge)) for edge in sol]
        edge_list.sort()
        return ", ".join(edge_list)

    def draw_graph(self, highlighted_edges):
        "Draw graph using_matplotlib"
        import matplotlib
        #if matplotlib.rcParams['backend'] == 'agg':
        matplotlib.rcParams['backend'] = self.backend
        
        import matplotlib.pyplot as plt
        G = self.graph
        
        pos=nx.spring_layout(G, weight = None)
        nx.draw_networkx_nodes(G,pos, node_size=330)
        nx.draw_networkx_edges(G,pos, set(G.edges()) - set(highlighted_edges), width=2)
        nx.draw_networkx_edges(G,pos, highlighted_edges, width=3, edge_color='blue')
        nx.draw_networkx_labels(G,pos, font_size=12, font_family='sans-serif')

        plt.draw()
        plt.show()

    def present_solution(self, sol):
        "Save solution to a file, and if necesssary draw it."
        
        with self.output_file as f:
            f.write( self.repr_solution(sol) + '\n' )

        if self.visualize:
            self.draw_graph(sol)
