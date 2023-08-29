import random
import copy
import networkx as nx
import matplotlib.pyplot as plt
import csv
import difflib
import pandas as pd
import math
import timeit

# Karger’s Algorithm
def kargerMinCut(graph, n):
    gn = { k : str(i) for (i, k) in enumerate(graph.keys(), 0)}
    while len(graph) > n:
         v = random.choice(list(graph.keys())) # the key
         w = random.choice(graph[v]) # the list of connections

         # assigning the same label to the nodes that are being grouped
         label = gn[w]
         for key in gn.keys():
             if(gn[key] == label):
                 gn[key] = gn[v]

         contract(graph, v, w) # merge together

    mincut = len(graph[list(graph.keys())[0]]) # calculate mincut
    return (gn, mincut)

def contract(graph, v, w):
    for node in graph[w]:  # merge the nodes from w to v
         if node != v:  # we don't want to add self-loops
             graph[v].append(node)
         graph[node].remove(w)  # delete the edges to the absorbed 
         if node != v:
              graph[node].append(v)
    del graph[w]  # delete the absorbed vertex 'w'

# load csv data
def load_data():
    return {int(str(line[0]).replace('[', '').replace(']', '')) : [int(str(i).replace('[', '').replace(']', '')) for i in line[1:]] for line in csv.reader(open("dataSmall.csv"))}


def DataToGraphDict(data, threshold): # compares users by comunities that they follow
    g = {}
    for i, (k1, v1) in enumerate(data.items(), 1):
        for k2, v2 in list(data.items())[i:]:
            if k1 != k2:
                sm = difflib.SequenceMatcher(None, v1, v2)
                if sm.ratio() > threshold:
                    g[k1] = g.get(k1, []) + [k2]
                    g[k2] = g.get(k2, []) + [k1]
        print("data processing: ", i, "/", len(data.keys()))
    return g

dpstart = timeit.default_timer()
g = DataToGraphDict(load_data(), 0.05)
dpend = timeit.default_timer()
print("data processing finished, took: ", dpend - dpstart, "s")

def main(g, n): # n is a number of groups we want to divide our dataset into
    res = {} # labels user id to groups, { id: group }
    cuts = []
    iterations = len(list(g.keys())) * int(math.log(len(list(g.keys())), 2)) # number of interations for great result
    for i in range(iterations):
        labels, mincut = kargerMinCut(copy.deepcopy(g), n) # run
        cuts.append(mincut)
        if min(cuts) == mincut:
            res = labels
    
        print(i, "/", iterations)

    print("minimum cuts: ", min(cuts))
    return res
    
KargerStart = timeit.default_timer()
labelsData = main(g, 12)
KargerEnd = timeit.default_timer()
print("Karger clusterization finished, took: ", KargerEnd - KargerStart, "s")

# check how many elements are in each group
ne = {}
for k, v in labelsData.items():
    ne[v] = ne.get(v, 0) + 1
print("number of entries of labels: ", ne)


# construct graph for visualization
edges = []
for k, v in g.items():
    for e in v:
        edges.append(tuple([k,e]))
G = nx.Graph()
G.add_edges_from(edges)


# color the graph
carac = pd.DataFrame({ 'ID': list(labelsData.keys()), 'groups': list(labelsData.values()) })
carac = carac.set_index('ID')
carac = carac.reindex(G.nodes())
carac['groups'] = pd.Categorical(carac['groups'])
carac['groups'].cat.codes

# draw the graph
nx.draw(G, labels = labelsData, with_labels = "True", node_color = carac['groups'].cat.codes, cmap = plt.cm.Set1, node_size = 140)
#plt.savefig("graph.png")
plt.show()