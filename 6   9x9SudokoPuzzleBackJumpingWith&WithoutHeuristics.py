#6.3.3 implement with and without heuristics.compare seaRch space and tc
#implement 9 9 sudoko

#But in Sudoku (dense constraints), sometimes they tie.

#for execution time calc
import time
#to make its own copy without modifying the original)
import copy
#for memory usage calc
import tracemalloc

class SudokuSolver:
    def __init__(self, board):
        self.board = board
        #number of recursive calls
        self.steps = 0
    
    #is_valid checks if placing num in (row, col) is allowed.
    def is_valid(self, row, col, num):
        # Row & Column check
        for i in range(9):
            if self.board[row][i] == num or self.board[i][col] == num:
                return False
            
        # 3x3 Subgrid check
        #for top left corner
        sr, sc = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if self.board[sr+i][sc+j] == num:
                    return False
        return True


# ------------------- 1. Simple Backtracking -------------------
class SimpleBacktracking(SudokuSolver):
    def solve(self):
        self.steps += 1
        #loos thru eah cell.if cell is empty(0) then try numbers in it.
        for row in range(9):
            for col in range(9):
                if self.board[row][col] == 0:
                    #1-9
                    for num in range(1, 10):
                        if self.is_valid(row, col, num):
                            self.board[row][col] = num
                            #Calls recursion: if later success → propagate True.Otherwise, undo assignment (backtrack).
                            if self.solve():
                                return True
                            self.board[row][col] = 0
                    return False
        return True


# ------------------- 2. Heuristic Backtracking (MRV) -------------------
class HeuristicBacktracking(SudokuSolver):
    def find_mrv(self):
        #best stores best cell.min_cand=10 (larger than max possible candidates=9)
        best = None
        min_cand = 10
        #For each empty cell, compute list of valid numbers (cand).
        for row in range(9):
            for col in range(9):
                if self.board[row][col] == 0:
                    cand = [num for num in range(1, 10) if self.is_valid(row, col, num)]
                    #Keep track of the cell with fewest options.Returns (row, col, candidates).
                    if len(cand) < min_cand:
                        min_cand = len(cand)
                        best = (row, col, cand)
        return best

    def solve(self):
        #Each recursion increments steps.Finds best cell using MRV.
        self.steps += 1
        cell = self.find_mrv()
        #If no empty cell found → solved.
        if not cell:
            return True
        #Tries each candidate, backtracking if needed.
        row, col, cand = cell
        for num in cand:
            self.board[row][col] = num
            if self.solve():
                return True
            self.board[row][col] = 0
        return False


# ------------------- 3. Backjumping (Fixed) -------------------
#Backjumping is an improved version of backtracking that tries to “jump back” multiple steps at once instead of undoing just the most recent move.
class Backjumping(SudokuSolver):
    #__init__ calls parent constructor to set self.board and self.steps
    def __init__(self, board):
        super().__init__(board)
        #self.empty_cells is a precomputed list of coordinates for all empty cells, in a fixed linear order. This index-based ordering lets us refer to "variable index idx".
        self.empty_cells = [(i, j) for i in range(9) for j in range(9) if self.board[i][j] == 0]
         # conflict_sets[idx] will collect indices (or markers) that represent which earlier variables contributed to failures encountered when trying to fill empty_cells[idx].
        self.conflict_sets = [set() for _ in range(len(self.empty_cells))]


    #assigns values to the idx th empty cell    
    def recursive_ibt(self, idx):
        self.steps += 1
   
        # BASE CASE:if idx equals the number of empty cells, all were filled successfully → puzzle solved.
        if idx == len(self.empty_cells):
            return True, idx   # return tuple both success + jump index
        
        #Retrieve coordinates (row, col) for the current empty cell.
        row, col = self.empty_cells[idx]

        # try all numbers 1-9
        for num in range(1, 10):
            if self.is_valid(row, col, num):
                self.board[row][col] = num
                solved, jump_to = self.recursive_ibt(idx + 1)#next empty cell
                if solved:
                    return True, jump_to
                
                # merge conflict sets
                self.conflict_sets[idx] |= self.conflict_sets[jump_to] #union the set at jump_to into the set at idx
                self.board[row][col] = 0 #backtrack
                #After merging, if the current index idx appears in its own conflict set, that means current variable is implicated in the failure and cannot resolve it by trying other values.So we signal a backjump by returning (False, idx) — saying: "I failed and the conflict points to idx (so callers should consider idx)."
                if idx in self.conflict_sets[idx]:
                    # must backjump
                    return False, idx

        # ❌ no candidate worked → backjump
        #If loop finished with no num leading to success, no candidate works here.Mark current index as conflicting (self.conflict_sets[idx].add(idx)) to record that this variable itself caused failure.Return (False, idx - 1) — communicates failure and suggests jumping back to idx-1.
        self.conflict_sets[idx].add(idx)
        return False, idx - 1   # jump back to earlier cell

#Public method to start recursion from the first empty cell.Unpacks the returned pair and returns only the boolean solved to caller.
    def solve(self):
        solved, _ = self.recursive_ibt(0)
        return solved

# ------------------- 4. Backjumping + Heuristic (Fixed) -------------------
class BackjumpingHeuristic(SudokuSolver):
    def __init__(self, board):
        super().__init__(board)
        self.conflict_sets = {}   # track conflicts per cell

    def find_mrv(self):
        """Pick cell with Minimum Remaining Values (MRV)."""
        best = None
        min_cand = 10
        candidates = None
        for row in range(9):
            for col in range(9):
                if self.board[row][col] == 0:
                    cand = [num for num in range(1, 10) if self.is_valid(row, col, num)]
                    if len(cand) < min_cand:
                        min_cand = len(cand)
                        best = (row, col)
                        candidates = cand
        return best, candidates

    def recursive_bjh(self, path):
        """path = list of assigned cells in order"""
        self.steps += 1

        # ✅ all cells filled → solved
        cell, cand = self.find_mrv()
        if not cell:
            return True, None   # solved, no jump

        row, col = cell
        for num in cand:
            if self.is_valid(row, col, num):
                self.board[row][col] = num
                solved, jump_cell = self.recursive_bjh(path + [(row, col)])
                if solved:
                    return True, None
                # merge conflict info
                self.conflict_sets[(row, col)] = self.conflict_sets.get((row, col), set())
                self.conflict_sets[(row, col)].add(num)
                self.board[row][col] = 0

                # If conflict points to an earlier cell → backjump
                if jump_cell and jump_cell != (row, col):
                    return False, jump_cell

        # ❌ no candidate worked
        if path:
            # backjump to the *earliest conflict in path*
            return False, path[-1]
        else:
            return False, None

    def solve(self):
        solved, _ = self.recursive_bjh([])
        return solved

# ------------------- Run & Compare -------------------
#Runs any solver class (Cls) on a fresh copy of board.Measures runtime using time.time().Also tracks memory usage with tracemalloc.
def run_solver(Cls, board, name):
    solver = Cls(copy.deepcopy(board))
    tracemalloc.start()
    start = time.time()
    solver.solve()
    end = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "Algorithm": name,
        "Steps": solver.steps,
        "Time (s)": end - start,
        "Memory (KB)": round(peak / 1024, 2)   # convert bytes → KB
    }


if __name__ == "__main__":
    # Example Sudoku (0 = empty)
    board = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]
   #Runs all four solvers.Appends results to list.
    results = []
    results.append(run_solver(SimpleBacktracking, board, "Simple Backtracking"))
    results.append(run_solver(HeuristicBacktracking, board, "Heuristic Backtracking"))
    results.append(run_solver(Backjumping, board, "Backjumping"))
    results.append(run_solver(BackjumpingHeuristic, board, "Backjumping + Heuristic"))

    # ---------------- Tabulate Results ----------------
    print("\nResults:")
    #:<25 → left-align algorithm name in 25 spaces.   :>10 → right-align numbers in 10 spaces.
    print(f"{'Algorithm':<25} | {'Steps':>10} | {'Time (s)':>10} | {'Memory (KB)':>12}")
    print("-"*65)
    for row in results:
        print(f"{row['Algorithm']:<25} | {row['Steps']:>10} | {row['Time (s)']:>10.4f} | {row['Memory (KB)']:>12.2f}")
