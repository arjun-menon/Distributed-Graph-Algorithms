
import networkx as nx
import matplotlib
matplotlib.rcParams['backend'] = "Qt4Agg"
import matplotlib.pyplot as plt

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

T=nx.minimum_spanning_tree(G)

for e in T.edges():
    print(e)

def draw_G(G, select_edges=[]):
    pos=nx.spring_layout(G, weight = None)
    nx.draw_networkx_nodes(G,pos, node_size=300)
    nx.draw_networkx_edges(G,pos, set(G.edges()) - set(select_edges), width=2)
    nx.draw_networkx_edges(G,pos, select_edges, width=3, edge_color='blue')
    nx.draw_networkx_labels(G,pos, font_size=12, font_family='sans-serif')

draw_G(G, T.edges())

plt.draw()
plt.show()

