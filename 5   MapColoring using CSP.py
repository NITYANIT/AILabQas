#A planar graph is a graph that can be drawn on a flat plane (a sheet of paper) without any edges crossing each other

#Map coloring problem uses planar graphs:
#Each country is a node, borders are edges. Planar property ensures that 4 colors are enough to color any map (the Four Color Theorem).
import time
import tracemalloc
import sys

# Increase recursion limit,generally does upto 100
sys.setrecursionlimit(50000)

# ---------------- Graph Generator ----------------
def generate_planar_graph(rows=10, cols=10):
    #rows * cols = number of nodes.
    n = rows * cols
    #dictionary key→ each node has a set of neighbors
    adjacency = {i: set() for i in range(n)}
    #{0: {1}, 1: {0}, 2: set(), 3: set()}

    # Add edges in a grid  building a 2d grid
    for r in range(rows):
        for c in range(cols):
            #row_index * number_of_columns + column_index  uniq id of each node
            #Why does this work?Each row has cols elements.So if you’re on row r, you’ve already "skipped" r * cols cells from the rows above.Then, you add the column index c to reach the exact position.
            node = r * cols + c
            #If we are not in the last column(both directions.as it is undirected)
            if c + 1 < cols:
                right = node + 1
                adjacency[node].add(right)
                adjacency[right].add(node)
                #If we are not in the last row,connect this node to the one below it.
            if r + 1 < rows:
                down = node + cols
                adjacency[node].add(down)
                adjacency[down].add(node)

    # add Diagonals edges (checkerboard rule)
    #We stop at rows - 1 and cols - 1(This would cause index out of range errors.) because each diagonal needs a 2×2 square block.
    for r in range(rows - 1):
        for c in range(cols - 1):
            # Label the corners of the 2×2 square
            a = r * cols + c  #TL----
            b = a + 1          #TR
            d = a + cols       #BL
            e = d + 1          #BR
          #If r+c is even → connect a ↔ e (top-left ↔ bottom-right). If r+c is odd → connect b ↔ d (top-right ↔ bottom-left).
          #Instead, we connect only one diagonal per 2×2 block, alternating like a checkerboard.
            if (r + c) % 2 == 0:
                adjacency[a].add(e)
                adjacency[e].add(a)
            else:
                adjacency[b].add(d)
                adjacency[d].add(b)
                #Example with (r+c) % 2
#2×2 grid block with (r=0,c=0):
#a(0,0) —— b(0,1)          
# |          |
#c(1,0) —— d(1,1)
#Here (r+c) = 0+0 = 0 (even) → connect a–d.
#Next block (r=0,c=1):
#b(0,1) —— x(0,2)
# |           |
#d(1,1) —— y(1,2)
#Here (r+c) = 0+1 = 1 (odd) → connect b–d instead.
#So it alternates diagonals like a checkerboard ✅

    return adjacency

# ---------------- CSP Backtracking ----------------
def is_consistent(node, color, assignment, graph):
    #Check if assigning 'color' to 'node' is valid wrt neighbors.
    for neighbor in graph[node]:
        if neighbor in assignment and assignment[neighbor] == color:
            return False
    return True
#assignment → dictionary storing nodes with assigned colors.
#variables → list of all nodes.
#domains → possible colors for each node.
#graph → adjacency list.
#start + timeout → to stop if it takes too long.
#timeout → is the maximum time allowed (in seconds).
def backtrack(assignment, variables, domains, graph, start, timeout=10):
    """Recursive backtracking search with MRV + timeout."""
    #If all nodes are assigned → we found a valid solution.
    if len(assignment) == len(variables):
        return assignment

    #If it runs longer than timeout seconds → abort search.
    if time.time() - start > timeout:
        return None
    # MRV heuristic: pick variable with fewest remaining colors
    unassigned = [v for v in variables if v not in assignment]
    node = min(unassigned, key=lambda var: len(domains[var]))

    for color in domains[node]:
        if is_consistent(node, color, assignment, graph):
            assignment[node] = color
            result = backtrack(assignment, variables, domains, graph, start, timeout)
            if result is not None:
                return result
            del assignment[node]  # backtrack

    return None
#--------solver--------
def solve_map_coloring(graph, colors=4, timeout=10):
    variables = list(graph.keys())
    domains = {v: list(range(colors)) for v in variables}
    assignment = {}
    start = time.time()#current time in sec
    return backtrack(assignment, variables, domains, graph, start, timeout)

# ---------------- Benchmark Function ----------------
def benchmark(rows, cols, colors=4, timeout=10):
    graph = generate_planar_graph(rows, cols)
    n = len(graph)

    print(f"\nRunning CSP-Backtracking Map Coloring on graph with {n} nodes")

    tracemalloc.start()
    start = time.time()

    solution = solve_map_coloring(graph, colors, timeout)

    end = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "Nodes": n,
        #graph is your adjacency list (dict: node → set of neighbors)For each node, len(v) = number of neighbors (degree of that node).So sum(len(v) for v in graph.values()) = sum of all degrees in the graph.Handshaking Lemma 🖐️Sum of degrees of all vertices=2×Number of edgesAdjacency list:
#{
 # 0: {1, 2},
  #1: {0, 2},
  #2: {0, 1}
#}
#Degrees: len(0)=2, len(1)=2, len(2)=2 → sum = 6
#But actual edges = {0-1, 1-2, 0-2} → only 3
#So sum(...) // 2 = 6 // 2 = 3 
        "Edges": sum(len(v) for v in graph.values()) // 2,
        "Time (s)": round(end - start, 3),#round(x, 3) → round to 3 decimal places.
        "Memory (KB)": round(peak / 1024, 2),
        "Success": solution is not None#did we solve it or not(just a boolean flag to record whether the backtracking search actually found a solution.)
    }

# ---------------- Run Experiments ----------------
results = []
results.append(benchmark(10, 10, timeout=10))     # ~100 nodes
results.append(benchmark(32, 32, timeout=15))     # ~1000 nodes
results.append(benchmark(100, 100, timeout=20))   # ~10000 nodes (may timeout)

# ---------------- Tabulate Results ----------------
print("\nResults:")
print(f"{'Nodes':>10} | {'Edges':>10} | {'Time (s)':>10} | {'Memory (KB)':>12} | {'Success':>8}")
print("-"*60)
for row in results:
    print(f"{row['Nodes']:>10} | {row['Edges']:>10} | {row['Time (s)']:>10} | {row['Memory (KB)']:>12} | {row['Success']}")
