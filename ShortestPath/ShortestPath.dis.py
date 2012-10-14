'''
Straightforward distributed shortest path finder based on Dijkstra's sequential algorithm
'''

from InputGraph import graph_source_target

G, S, T = graph_source_target()

INFINITY = 999999999

class P(DistProcess):
    
    def setup(ps, edges):
        edges = edges
        weight = INFINITY
        path = ""

    def OnNewWeight(new_weight, new_path):
        newWeight(new_weight, new_path)

    def newWeight(new_weight, new_path):
        if new_weight < weight:
            weight = new_weight
            path = new_path
            if str(self) == T:
                output("New shortest path of weight %i: %s" 
                    % (weight, ' -> '.join(path)))
            propogate()

    def propogate():
        for p, e_w in edges.items():
            send(NewWeight(weight + e_w, path+str(p)), p)

    def main():
        if str(self) == S:
            newWeight(0, str(self))
        await(False)

def main():
    use_channel("tcp")
    
    procs_names = set(G.nodes())
    #procs_names.update({'0'})# control process
    
    global procs
    procs = createprocs(P, procs_names)
    
    # setup the processes
    ps = set(procs.values())
    
    for p in ps:
        p_edges = { procs[node] : data['weight'] 
            for (node, data) in G[repr(p)].items() }
        setupprocs([p], [ps-{p}, p_edges])
    
    startprocs(ps)
    
    for p in (ps):
        p.join()
