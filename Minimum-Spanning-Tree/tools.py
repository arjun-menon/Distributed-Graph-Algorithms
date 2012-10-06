
import sys
sys.path.append('..')
import networkx as nx

def construct_graph(numbered=False):
    n = 13
    A, B, C, D, E, F, G, H, I, J, K, L, M = (
             [str(i+1)        for i in range(n)] if numbered 
        else [chr(ord('A')+i) for i in range(n)])
    
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
    edge(D,B,16),

    edge(L,M,20),
    edge(K,L,21),
    edge(K,M,22),
    edge(J,K,23),
    ]
    
    G = nx.Graph()
    G.add_edges_from(edge_list)
    
    #for e in G.edges(data=True):
    #    print(e)
    return G

def verify_solution(G, sol):
    '''Verify the solution for MST against NetworkX's built-in MST solver.
       Only works if the solution is unique (=> edges have unique weights.)'''
    
    nx_sol = set( nx.minimum_spanning_tree(G).edges() )
    
    return nx_sol == sol

def draw_graph_using_matplotlib(G, highlighted_edges, backend='Qt4Agg'):
    import matplotlib
    if matplotlib.rcParams['backend'] == 'agg':
        matplotlib.rcParams['backend'] = backend
    
    import matplotlib.pyplot as plt
    
    pos=nx.spring_layout(G, weight = None)
    nx.draw_networkx_nodes(G,pos, node_size=330)
    nx.draw_networkx_edges(G,pos, set(G.edges()) - set(highlighted_edges), width=2)
    nx.draw_networkx_edges(G,pos, highlighted_edges, width=3, edge_color='blue')
    nx.draw_networkx_labels(G,pos, font_size=12, font_family='sans-serif')

    plt.draw()
    plt.show()

def render_solution(sol):   
    edge_list = ["(%s, %s)" % (min(edge), max(edge)) for edge in sol]
    edge_list.sort()
    return ", ".join(edge_list)

def test_visualize_optarg():
    if len(sys.argv) > 1 and sys.argv[1] == '-v':
        return True
    elif len(sys.argv) > 1 and sys.argv[1] == '-V':
        return False
    else:
        print("To visualize the graph and its solution using matplotlib, use the optarg -v")    
        return False
