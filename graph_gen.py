#!/usr/bin/python3

'''
Random graph generator

It works by constructing a partial adjacency matrix of the preferred number of nodes, 
then filling the adjacency matrix with random 0 or 1 values.
'''
import random

def max_edges(n):
    """
    Maximum number of egdges in undirected acyclic graph.

    If you throw away the diagonal and everything below it in 
    the adjacency matrix, the number valid colums in each row 
    for a 6x6 adj. matrix is: 5 + 4 + 3 + 2 + 1 -- ie. sum of  
    the natural numbers[*] from 1 to (n-1).

    [*] Sum of n natural numbers = n * (n + 1) / 2
    """

    return ((n-1) * (n))/ 2

def enumerate_edges(n):
    e = []
    for i in range(1, n):
        for j in range(i+1, n+1):
            e += [(i,j)]
    return e

def random_edges(max_nodes, edge_count):
    all_edges = enumerate_edges(max_nodes)

    return random.sample(all_edges, edge_count)

def random_weighted_edges(max_nodes, edge_count):
    def edge(n1, n2, w):
            return (n1, n2, {'weight':w})

    rg = random_edges(max_nodes, edge_count)

    random_weights = random.sample(range(1, len(rg)*10), len(rg))

    edges = []
    r_i = 0
    for (u, v) in rg:
        edges += [edge(u, v, random_weights[r_i])]
        r_i += 1

    return edges

def weighted_edges_to_file(g, fname):
    with open(fname, 'w') as f:
        for e in g:
            u, v, w = e
            f.write("%s %s %d\n" % (u, v, w['weight']))

def networkx_random_weighted_graph(n, e):
    """Generate a random NetworkX graph.

    n : The maximum number of nodes in the graph.
    e : The number of edges in the graph.
    """

    import sys
    sys.path.append('..')
    import networkx as nx

    G = nx.Graph()

    G.add_edges_from( random_weighted_edges(n, e) )

    random_attributes = random.sample(range(1, n*10), n)
    r_i = 0
    for n in G.nodes():
        G.node[n]['value'] = random_attributes[ r_i ]
        r_i += 1

    return G

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Generate a random graph.')
    parser.add_argument('-n', '--nodes', nargs=1, type=int, default=[6], help='The maximum number of nodes in the graph.')
    parser.add_argument('-e', '--edges', nargs=1, type=int, default=[10], help='The number of edges in the graph.')
    parser.add_argument('file_name', nargs='?', type=str, default='random_graph', help='File to write the graph to, listing the edges of a graph line-by-line in the following style: "A B 2", where "A" and "B" are node names and "2" is the weight of the edge connecting them.')
    args = parser.parse_args()
    n = args.nodes[0]
    print("Maximum possible number of edges is %d." % max_edges(n))
    e = args.edges[0]
    print("Out of which %d edges will be randomly chosen." % e)
    f = args.file_name

    rg = random_weighted_edges(n, e)
    print(rg)
    weighted_edges_to_file(rg, f)

    ng = networkx_random_weighted_graph(n, e)
    print(ng.nodes(data=True))
