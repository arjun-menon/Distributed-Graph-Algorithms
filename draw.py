#!/usr/bin/python3

import sys
file = sys.argv[1]

def edge(n1, n2, w):
    return (n1, n2, {'weight':w})

edge_list = list()

with open(file, 'r') as f:
    edge_list = list( edge(ed.split()[0], ed.split()[1], int(ed.split()[2])) 
        for ed in 
        (e.strip() for e in f.readlines() if e.strip() != "") 
        if len(ed.split()) == 3 )

    sys.path.append('..')
    import networkx as nx
    G = nx.Graph()
    G.add_edges_from(edge_list)

    "Draw graph using_matplotlib"
    import matplotlib
    if matplotlib.rcParams['backend'] == 'agg':
        matplotlib.rcParams['backend'] = 'Qt4Agg'
    
    import matplotlib.pyplot as plt    
    pos=nx.spring_layout(G, weight = None)
    nx.draw_networkx_nodes(G,pos, node_size=330)
    nx.draw_networkx_edges(G,pos, set(G.edges()), width=2)
    nx.draw_networkx_labels(G,pos, font_size=12, font_family='sans-serif')

    plt.draw()
    plt.show()
