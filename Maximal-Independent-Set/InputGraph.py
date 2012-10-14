
import sys
sys.path.append('..')
import networkx as nx

def get_graph():
    "Process command-line arguments and build the graph."

    sys.argv = sys.argv[1:]

    def construct_graph(file):
        def edge(n1, n2, w):
            return (n1, n2, {'weight':w})

        edge_list = list()

        with open(file, 'r') as f:
            edge_list = list( edge(ed.split()[0], ed.split()[1], int(ed.split()[2])) 
                for ed in 
                (e.strip() for e in f.readlines() if e.strip() != "") 
                if len(ed.split()) == 3 )

            G = nx.Graph()
            G.add_edges_from(edge_list)
            return G

    import argparse
    parser = argparse.ArgumentParser(description='Finds the vertices of the Maximal Independent Set (MST) of a given graph.')
    parser.add_argument('graph', nargs='?', type=construct_graph, default='graph-1', help=
'File listing the edges of a graph line-by-line in the following style: "A B 2", where "A" and "B" are node names and "2" is the weight of the edge connecting them.')

    args = parser.parse_args()
    return args.graph
