#to create&manage graphs
import networkx as nx
#to pick random nodes&generate random wts 
import random
#to get execution times of algos
import time
#not used
import pandas as pd
#used in ucs
from queue import PriorityQueue
#used in bfs for efficient algo
from collections import deque

# Ensure&generate the connected graph
def generate_connected_graph(n, edge_prob=0.01):
    while True:
        #generating the random graph 
        G = nx.erdos_renyi_graph(n, edge_prob)
        #checking connectivity of graph
        #we can also check the connectivity of a graph thru traversals(bfs/dfs) but the diff is who des it internally.now our import does it.
        if nx.is_connected(G):
            #if connected it assigns the random wts from 1-10 &return it 
            for (u, v) in G.edges():
                G.edges[u, v]['weight'] = random.randint(1, 10)
            return G

# BFS
def bfs(graph, start, goal):
    visited, queue = set(), deque([(start, [start])])
    nodes_generated = 0
    while queue:
        vertex, path = queue.popleft()
        nodes_generated += 1
        if vertex == goal:
            return path, nodes_generated
        if vertex not in visited:
            visited.add(vertex)
            for neighbor in graph.neighbors(vertex):
                queue.append((neighbor, path + [neighbor]))
    return None, nodes_generated

# DFS
def dfs(graph, start, goal):
    visited, stack = set(), [(start, [start])]
    nodes_generated = 0
    while stack:
        vertex, path = stack.pop()
        nodes_generated += 1
        if vertex == goal:
            return path, nodes_generated
        if vertex not in visited:
            visited.add(vertex)
            for neighbor in graph.neighbors(vertex):
                stack.append((neighbor, path + [neighbor]))
    return None, nodes_generated

# UCS
def ucs(graph, start, goal):
    visited = set()
    pq = PriorityQueue()
    pq.put((0, start, [start]))
    nodes_generated = 0
    while not pq.empty():
        cost, vertex, path = pq.get()
        nodes_generated += 1
        if vertex == goal:
            return path, nodes_generated, cost
        if vertex not in visited:
            visited.add(vertex)
            for neighbor in graph.neighbors(vertex):
                edge_cost = graph.edges[vertex, neighbor]['weight']
                pq.put((cost + edge_cost, neighbor, path + [neighbor]))
    return None, nodes_generated, float('inf')

# IDS
def dls(graph, current, goal, limit, path, visited, nodes_generated):
    nodes_generated[0] += 1
    if current == goal:
        return path
    if limit <= 0:
        return None
    visited.add(current)
    for neighbor in graph.neighbors(current):
        if neighbor not in visited:
            result = dls(graph, neighbor, goal, limit - 1, path + [neighbor], visited, nodes_generated)
            if result:
                return result
    visited.remove(current)
    return None

def ids(graph, start, goal):
    depth = 0
    nodes_generated = [0]
    while True:
        visited = set()
        result = dls(graph, start, goal, depth, [start], visited, nodes_generated)
        if result:
            return result, nodes_generated[0]
        depth += 1

# Main
n = 1000
G = generate_connected_graph(n)
#no of random source-dest pairs(3)
trials = 3
#dictionary with K-V pairs
results = {"Algorithm": [], "Avg Time": [], "Avg Nodes": [], "Avg Cost": []}

# store exetime,nonodes generated,cost
bfs_times, dfs_times, ucs_times, ids_times = [], [], [], []
bfs_nodes, dfs_nodes, ucs_nodes, ids_nodes = [], [], [], []
ucs_costs = []

for _ in range(trials):
    #consider random source-dest nodes
    src, dest = random.sample(range(n), 2)
    
    #storing execution time and no of nodes explored
    #path = path from src to dest
    #nodes = number of nodes explored
    #cost = total cost (sum of edge weights) of the path
    start_time = time.time()
    path, nodes = bfs(G, src, dest)
    bfs_times.append(time.time() - start_time)
    bfs_nodes.append(nodes)
    
    start_time = time.time()
    path, nodes = dfs(G, src, dest)
    dfs_times.append(time.time() - start_time)
    dfs_nodes.append(nodes)
    
    start_time = time.time()
    path, nodes, cost = ucs(G, src, dest)
    ucs_times.append(time.time() - start_time)
    ucs_nodes.append(nodes)
    ucs_costs.append(cost)
    
    start_time = time.time()
    path, nodes = ids(G, src, dest)
    ids_times.append(time.time() - start_time)
    ids_nodes.append(nodes)

# Prepare results
results["Algorithm"] = ["BFS", "DFS", "UCS", "IDS"]
results["Avg Time"] = [
    sum(bfs_times)/trials, sum(dfs_times)/trials, sum(ucs_times)/trials, sum(ids_times)/trials
]
results["Avg Nodes"] = [
    sum(bfs_nodes)/trials, sum(dfs_nodes)/trials, sum(ucs_nodes)/trials, sum(ids_nodes)/trials
]
#cost is only meaningful for ucs
results["Avg Cost"] = [
    None, None, sum(ucs_costs)/trials, None
]

# Print C-style table
print("\n=== Average Results ===")
print(f"{'Algorithm':<10} {'Avg Time (s)':<15} {'Avg Nodes':<12} {'Avg Cost':<10}")
print("-" * 50)
for i in range(len(results["Algorithm"])):
    print(f"{results['Algorithm'][i]:<10} {results['Avg Time'][i]:<15.6f} {results['Avg Nodes'][i]:<12.2f} {str(results['Avg Cost'][i] or '-'): <10}")   
