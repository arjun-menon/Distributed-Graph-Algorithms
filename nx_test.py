
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

G = nx.balanced_tree(2, 3)

print(G.nodes())
print(G.edges())

print(set( G.neighbors(1) ))
nx.freeze(G)
G.node[1]['parent'] = 0

print(G[0])

print(G.nodes(data=True))
print(G.node[1])
