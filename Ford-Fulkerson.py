from collections import defaultdict
import numpy as np
import timeit
import csv
import difflib

# This class represents a directed graph using adjacency matrix representation
class Graph:

    def __init__(self,graph):
        self.graph = graph # residual graph
        self.org_graph = [i[:] for i in graph]
        self. ROW = len(graph)
        self.COL = len(graph[0])


    '''Returns true if there is a path from source 's' to sink 't' in 
    residual graph. Also fills parent[] to store the path '''
    def BFS(self,s, t, parent):

        # Mark all the vertices as not visited
        visited =[False]*(self.ROW)

        # Create a queue for BFS
        queue=[]

        # Mark the source node as visited and enqueue it
        queue.append(s)
        visited[s] = True

        # Standard BFS Loop
        while queue:

            #Dequeue a vertex from queue and print it
            u = queue.pop(0)

            # Get all adjacent vertices of the dequeued vertex u
            # If a adjacent has not been visited, then mark it
            # visited and enqueue it
            for ind, val in enumerate(self.graph[u]):
                if visited[ind] == False and val > 0 :
                    queue.append(ind)
                    visited[ind] = True
                    parent[ind] = u

        # If we reached sink in BFS starting from source, then return
        # true, else false
        return True if visited[t] else False


    # Returns the min-cut of the given graph
    def minCut(self, source, sink):

        # This array is filled by BFS and to store path
        parent = [-1]*(self.ROW)

        max_flow = 0 # There is no flow initially

        # Augment the flow while there is path from source to sink
        while self.BFS(source, sink, parent) :

            # Find minimum residual capacity of the edges along the
            # path filled by BFS. Or we can say find the maximum flow
            # through the path found.
            path_flow = float("Inf")
            s = sink
            while(s != source):
                path_flow = min (path_flow, self.graph[parent[s]][s])
                s = parent[s]

            # Add path flow to overall flow
            max_flow += path_flow

            # update residual capacities of the edges and reverse edges
            # along the path
            v = sink
            while(v != source):
                u = parent[v]
                self.graph[u][v] -= path_flow
                self.graph[v][u] += path_flow
                v = parent[v]

        # print the edges which initially had weights
        # but now have 0 weight
        for i in range(self.ROW):
            for j in range(self.COL):
                if self.graph[i][j] == 0 and self.org_graph[i][j] > 0:
                    #print(str(i) + " - " + str(j))
                    pass


# load csv data
def load_data():
    return {int(str(line[0]).replace('[', '').replace(']', '')) : [int(str(i).replace('[', '').replace(']', '')) for i in line[1:]] for line in csv.reader(open("dataSmall.csv"))}

def DataToGraphDict(data, threshold): # compares users by comunities that they follow

    g = [[0 for l in range(len(data.keys()))] for l in range(len(data.keys()))]

    line = []
    for i, (k1, v1) in enumerate(data.items(), 0):
        for ix, (k2, v2) in enumerate(list(data.items())[i:], 0):
            if k1 != k2:
                sm = difflib.SequenceMatcher(None, v1, v2)
                if sm.ratio() > threshold:
                    g[i][ix] = sm.ratio()*100
                    g[ix][i] = sm.ratio()*100

        print("data processing: ", i, "/", len(data.keys()))

    return g

dpstart = timeit.default_timer()
graph = DataToGraphDict(load_data(), 0.05)
dpend = timeit.default_timer()
print("data processing finished, took: ", dpend - dpstart, "s")

g = Graph(graph)
source = 0; sink = len(graph)-1

fastart = timeit.default_timer()
for i in range(sink):
    for ix in range(sink):
        if i != ix:
            g.minCut(i, ix)
    print("iteration: ", i, "/", sink)

faend = timeit.default_timer()
print("Ford-Fulkerson Algorithm finished, took: ", faend - fastart, "s")