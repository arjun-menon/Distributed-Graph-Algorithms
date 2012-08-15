
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

print(G[0])
