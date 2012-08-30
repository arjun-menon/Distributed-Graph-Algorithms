#!/usr/bin/python3

import networkx as nx
from collections import deque

#q = deque()
#
#q.appendleft(1)
#q.appendleft(2)
#q.appendleft(3)
#
#print(q)
#
#print(q.pop())

####

#G = nx.balanced_tree(2, 3)
#
#print(G.nodes())
#print(G.edges())
#
#print(set( G.neighbors(1) ))
#nx.freeze(G)
#
#print(G[0])
#
#G.node[1]['parent'] = 0
#
#print(G.nodes(data=True))
#print(G.node[1])

####

import matplotlib
matplotlib.rcParams['backend'] = "Qt4Agg"
import matplotlib.pyplot as plt

g = nx.Graph()

g.add_nodes_from(range(1,11))

g.add_edge(1,2, w = 3)

G=nx.Graph()

G.add_edge('a','b',weight=0.6)
G.add_edge('a','c',weight=0.2)
G.add_edge('c','d',weight=0.1)
G.add_edge('c','e',weight=0.7)
G.add_edge('c','f',weight=0.9)
G.add_edge('a','d',weight=0.3)

print(G.edges())

elarge=[(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] >0.5]
esmall=[(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] <=0.5]

pos=nx.spring_layout(G) # positions for all nodes

# nodes
nx.draw_networkx_nodes(G,pos,node_size=700)

# edges
nx.draw_networkx_edges(G,pos,edgelist=elarge, width=2)
nx.draw_networkx_edges(G,pos,edgelist=esmall,
                    width=3,alpha=0.5,edge_color='b',style='dashed')

# labels
nx.draw_networkx_labels(G,pos,font_size=20,font_family='sans-serif')

plt.draw()
plt.show()

#####################################

#G = nx.Graph()
#edge_list = [
#    (1, 4, {'w':6}),
#    (1, 2, {'w':3.1}),
#    (1, 5, {'w':9.1}),
#
#    (2, 4, {'w':4.1}),
#    (2, 5, {'w':9.2}),
#    (2, 3, {'w':2.1}),
#
#    (2, 6, {'w':9.3}),
#    (3, 4, {'w':2.2}),
#    (3, 6, {'w':8.1}),
#    (6, 5, {'w':8.2}),
#
#    (3, 7, {'w':9.4}),
#    (4, 7, {'w':9.5}),
#
#    (5, 0, {'w':18}),
#    (6, 0, {'w':10}),
#
#    (6, 7, {'w':7}),
#    (6, 9, {'w':9.6}),
#    (7, 9, {'w':5}),
#
#    (7, 8, {'w':4.2}),
#    (8, 9, {'w':1}),
#    (9, 0, {'w':3.2}),
#    (8, 0, {'w':4.3}),
#]
#G.add_edges_from(edge_list)
#
#T=nx.minimum_spanning_tree(G)
#print(sorted(T.edges(data=True)))
#
#nx.draw(G)
#plt.draw()
#plt.show()
