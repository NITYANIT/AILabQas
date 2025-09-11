import heapq
import math
#for calcula execution time
import time
# Goal state
goal_state = [[1,2,3],[4,5,6],[7,8,0]]
goal_positions = {goal_state[i][j]:(i,j) for i in range(3) for j in range(3)}

# Heuristic: Manhattan distance
def manhattan(state):
    distance = 0
    for i in range(3):
        for j in range(3):
            val = state[i][j]
            if val != 0:
                gi, gj = goal_positions[val]
                distance += abs(i-gi) + abs(j-gj)
    return distance

#Get possible moves and then swap with neighbors
#get_neighbors = “from current board, generate all boards after moving the blank tile in each legal direction”.
def get_neighbors(state):
    neighbors = []
    #loop through and find the blank tile
    i, j = next((i,j) for i in range(3) for j in range(3) if state[i][j]==0)
    #DURL directions it can move
    moves = [(1,0),(-1,0),(0,1),(0,-1)]
    for di, dj in moves:
        #new blank positions
        ni, nj = i+di, j+dj
        #validation.preventing the out of bounds
        if 0 <= ni < 3 and 0 <= nj < 3:
            #copy of the current state
            new_state = [row[:] for row in state]
            #swwap the blank tile with other neighbor
            new_state[i][j], new_state[ni][nj] = new_state[ni][nj], new_state[i][j]
            neighbors.append(new_state)
    return neighbors

# Convert state to tuple of tuples to put in set (for hashing)
def to_tuple(state):
    return tuple(tuple(row) for row in state)

# ---------------- A* Search ---------------- #
#start positin of puzzle
def astar(start):
    #unexplored nodes
    frontier = []
    #priority q                f(n)            g(n) curr  path till now
    heapq.heappush(frontier, (manhattan(start), 0, start, []))
    explored = set()

    while frontier:
        #pick the best/min one
        f, g, state, path = heapq.heappop(frontier)
        #if curr is goal then return
        if state == goal_state:
            #ret path
            return path+[state]
        explored.add(to_tuple(state))
        #add possible states
        for neighbor in get_neighbors(state):
            if to_tuple(neighbor) not in explored:
                heapq.heappush(frontier,(g+1+manhattan(neighbor), g+1, neighbor, path+[state]))
    return None #unsolvable
#g(n) = how many steps you already walked.
#h(n) = how many steps you think are left.
#f(n) = total journey (walked + remaining).

# ---------------- RBFS ---------------- #
#Think of RBFS like “explore the best path first, but keep an eye on the 2nd best in case you need to backtrack.”
def rbfs(start):
    def rbfs_recursive(state, path, g, f_limit):
        #checks if goal
        if state == goal_state:
            return path+[state], 0
        successors = []
        for neighbor in get_neighbors(state):
            #ensures f doesn’t go backward (
            fval = max(g+1+manhattan(neighbor), g+1)
            successors.append([neighbor, path+[state], g+1, fval])
        if not successors:
            return None, math.inf
        while True:
            successors.sort(key=lambda x:x[3])
            #[3] comes coz you have indexes in successors
            best = successors[0]
            if best[3] > f_limit:
                return None, best[3]
            alternative = successors[1][3] if len(successors)>1 else math.inf
            result, best[3] = rbfs_recursive(best[0], best[1], best[2], min(f_limit, alternative))
            if result is not None:
                return result, 0
            #Start recursion with empty path, cost=0, and infinite f-limit
    return rbfs_recursive(start, [], 0, math.inf)[0]

# ---------------- Test ---------------- #
start_state = [[1,2,3],[5,0,6],[4,7,8]]

print("Solving with A*:")
t1 = time.time()
path_astar = astar(start_state)
t2 = time.time()
for s in path_astar:
    for row in s: print(row)
    print()

print("Solving with RBFS:")
t3 = time.time()
path_rbfs = rbfs(start_state)
t4 = time.time()
for s in path_rbfs:
    for row in s: print(row)
    print()

# ---------------- Performance Summary ---------------- #
# Cost = number of steps (path length - 1)
cost_astar = len(path_astar) - 1 if path_astar else None
cost_rbfs = len(path_rbfs) - 1 if path_rbfs else None
time_astar = (t2 - t1) * 1000
time_rbfs = (t4 - t3) * 1000

# Print results as a simple table (no extra libraries needed)
print("\n------ Performance Comparison ------")
print(f"{'Algorithm':<10} | {'Cost (steps)':<12} | {'Execution Time (ms)':<20}")
print("-" * 50)
print(f"{'A*':<10} | {cost_astar:<12} | {time_astar:<20.3f}")
print(f"{'RBFS':<10} | {cost_rbfs:<12} | {time_rbfs:<20.3f}")
