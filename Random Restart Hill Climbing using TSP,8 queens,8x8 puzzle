import random
import math
#taking a copy of nested lists
import copy
import time
#used to print tables in a nice formatted way (instead of just raw lists).
from tabulate import tabulate

# ---------------------- Random Restart Hill Climbing ----------------------
#The problem object (TSP, 8-puzzle, or 8-queens).
#no of times to restart the hill climbing from diff random initial state
#Maximum steps allowed per restart (to prevent infinite loops).
def random_restart_hill_climb(problem, restarts=10, max_steps=1000):
    #Stores the overall best solution found across all restarts.
    best_solution = None
    #Stores the lowest cost found so far, initialized to infinity so any real solution will be better.
    best_cost = float('inf')

    for r in range(restarts):
        #This is the key idea of random restart → avoid local minima.
        current = problem.random_state()
        for step in range(max_steps):
            neighbors = problem.get_neighbors(current)
            #stop climbing.
            if not neighbors:
                break
            #Choose the best neighbor (lowest cost) among all neighbors.
            next_state = min(neighbors, key=problem.cost)
            if problem.cost(next_state) < problem.cost(current):
                current = next_state
            else:
                break

        current_cost = problem.cost(current)
        if current_cost < best_cost:
            best_solution = current
            best_cost = current_cost

    return best_solution, best_cost

# ---------------------- Travelling Salesman Problem ----------------------
class TSP:
    #constructor
    def __init__(self, cities):
        #cities: List of city names
        self.cities = cities
        #A distance matrix between cities, generated randomly by _generate_distances()
        self.distances = self._generate_distances()

    def _generate_distances(self):
        #Number of cities.
        n = len(self.cities)
        #2d list
        distances = [[0]*n for _ in range(n)]
        for i in range(n):
            for j in range(i+1, n):
                d = random.randint(1, 50)
                #distances[i][j] = distances[j][i] = d (because distance from A→B = B→A)
                distances[i][j] = distances[j][i] = d
        return distances

    def random_state(self):
        #Creates a random order of visiting cities (a permutation).
        state = list(range(len(self.cities)))
        random.shuffle(state)
        return state

    def cost(self, state):
        total = 0
        for i in range(len(state)):
           #state[(i+1) % len(state)]: Wraps around so the last city connects back to the first (making it a cycle).
            total += self.distances[state[i]][state[(i+1) % len(state)]]
        return total
#If state = [0, 2, 1], cost = dist[0][2] + dist[2][1] + dist[1][0].
#If state = [0, 1, 2], neighbors are:
#Swap(0,1) → [1, 0, 2]
#Swap(0,2) → [2, 1, 0]
#Swap(1,2) → [0, 2, 1]
#A state = one possible route visiting all cities.
# Why is this useful?
#Searching all possible routes directly is too expensive (factorial growth: n! possibilities).
#So we use local search → explore only small modifications (neighbors).
#Swapping gives us a structured way to explore different paths step by step.
    def get_neighbors(self, state):
        neighbors = []
        for i in range(len(state)):
            for j in range(i+1, len(state)):
                neighbor = state[:]
                neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
                neighbors.append(neighbor)
        return neighbors

# ---------------------- 8 Queens Problem ----------------------
class EightQueens:
    #Creates a random board configuration.
#Representation: a list of length 8 → state[col] = row.
    def random_state(self):
        return [random.randint(0, 7) for _ in range(8)]
#Goal: Count number of attacking queen pairs.
#Loop through all pairs of queens (i, j):
#state[i] == state[j] → both in same row → conflict.
#abs(state[i] - state[j]) == abs(i - j) → diagonal conflict.
#conflicts = total pairs of queens attacking each other.
#Lower cost = better. Goal = cost = 0 (solution).
    def cost(self, state):
        conflicts = 0
        for i in range(len(state)):
            for j in range(i+1, len(state)):
                if state[i] == state[j] or abs(state[i]-state[j]) == abs(i-j):
                    conflicts += 1
        return conflicts

    def get_neighbors(self, state):
        neighbors = []
        #pick a queen’s column.
        for col in range(8):
            #try placing that queen in every row.
            for row in range(8):
                #don’t keep the same position.
                if state[col] != row:
                    #copy current state
                    neighbor = state[:]
                    #move queen in that column to a different row
                    neighbor[col] = row
                    neighbors.append(neighbor)
        return neighbors

# ---------------------- 8 Puzzle Problem ----------------------
class EightPuzzle:
    goal_state = [[1,2,3],[4,5,6],[7,8,0]]
   
    def random_state(self):
        state = [i for i in range(9)]
        #to generate a new arrangement.
        random.shuffle(state)
        #Convert the 1-D shuffled list into a 3x3 matrix.
        return [state[0:3], state[3:6], state[6:9]]

    def cost(self, state):
        #This is the “cost” of how far the current state is from the goal.
        cost = 0
        for i in range(3):
            for j in range(3):
                val = state[i][j]
                if val != 0:
                    goal_x, goal_y = divmod(val-1, 3)
                    cost += abs(goal_x - i) + abs(goal_y - j)
        return cost

    def get_neighbors(self, state):
        neighbors = []
        x = y = 0
        for i in range(3):
            for j in range(3):
                if state[i][j] == 0:
                    x, y = i, j
        moves = [(0,1),(1,0),(0,-1),(-1,0)]
        for dx, dy in moves:
            nx, ny = x+dx, y+dy
            if 0 <= nx < 3 and 0 <= ny < 3:
                new_state = copy.deepcopy(state)
                new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
                neighbors.append(new_state)
        return neighbors
    #random_state() → gives random puzzle.
#cost(state) → gives heuristic Manhattan distance.
#get_neighbors(state) → gives all states after sliding one tile.

def main():
    results = []

    # Travelling Salesman Problem
    cities = ["A","B","C","D","E"]
    problem = TSP(cities)
    t1 = time.time()
    solution, cost = random_restart_hill_climb(problem, restarts=10, max_steps=500)
    t2 = time.time()
    results.append(["TSP", cost, f"{(t2 - t1)*1000:.3f} ms"])

    # 8 Queens Problem
    problem = EightQueens()
    t3 = time.time()
    solution, cost = random_restart_hill_climb(problem, restarts=10, max_steps=500)
    t4 = time.time()
    results.append(["8-Queens", cost, f"{(t4 - t3)*1000:.3f} ms"])

    # 8 Puzzle Problem
    problem = EightPuzzle()
    t5 = time.time()
    solution, cost = random_restart_hill_climb(problem, restarts=10, max_steps=500)
    t6 = time.time()
    results.append(["8-Puzzle", cost, f"{(t6 - t5)*1000:.3f} ms"])

    # Print performance comparison table
    headers = ["Algorithm", "Cost", "Execution Time"]
    print("\n------ Performance Comparison ------")
    print(tabulate(results, headers=headers, tablefmt="grid"))

if __name__ == "__main__":
    main()
