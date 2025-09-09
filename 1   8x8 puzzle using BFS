from collections import deque
N = 3
class PuzzleState:
    def __init__(self, board, x, y, depth, path):
          # constructor
        self.board = board
        self.x = x
        self.y = y
        self.depth = depth
        # list of moves
        self.path = path  
 # directions
row = [0, 0, -1, 1]
col = [-1, 1, 0, 0]
moves = ['left', 'right', 'up', 'down']

def isGoalState(board):
    goal = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    return board == goal

def isValidState(x, y):
    return 0 <= x < N and 0 <= y < N

def printBoard(board):
    for row in board:
        # convert first into str and then give spaces in btwn for clarity
        print(' '.join(map(str, row)))

def issolvable(board):
    # remove zero
    flat_list = [num for row in board for num in row if num != 0]
    inversions = 0
    for i in range(len(flat_list)):
        for j in range(i + 1, len(flat_list)):
            if flat_list[i] > flat_list[j]:
                inversions += 1

    # solvable if inversions are even else odd.
    return inversions % 2 == 0


def solvePuzzleBfs(start, x, y):  
    q = deque()
    visited = set()
    q.append(PuzzleState(start, x, y, 0, []))
    # 2d tuple thing
    visited.add(tuple(map(tuple, start)))

    while q:
         # must add braces after popleft
        curr = q.popleft()
        # after evry iteration 1st check whether it has reached the goal
        if isGoalState(curr.board):
             # withut f str it wont evaluate depth variable
            print(f'\nGoal Reached at depth: {curr.depth}')
            print(f'Solution path: {curr.path}')
            print(f'Number of steps: {len(curr.path)}')
            return

        for i in range(4):
            newx = curr.x + row[i]
            newy = curr.y + col[i]

            if isValidState(newx, newy):
                 #    individually adds the each row
                newboard = [r[:] for r in curr.board]
                  # swap 0 with the target cell
                newboard[curr.x][curr.y], newboard[newx][newy] = newboard[newx][newy], newboard[curr.x][curr.y]
                if tuple(map(tuple, newboard)) not in visited:
                    visited.add(tuple(map(tuple, newboard)))
                    # Append current move to path
                    new_path = curr.path + [moves[i]]
                    q.append(PuzzleState(newboard, newx, newy, curr.depth + 1, new_path))

    print(' No solution found (BFS reached depth limit)')

if __name__ == '__main__':  
    start = [[1, 2, 3], [4, 0, 5], [6, 7, 8]]
    goal = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    x, y = 1, 1
    print('Initial State:')
    printBoard(start)
    print('\nGoal State:')
    printBoard(goal)
    solvePuzzleBfs(start, x, y)
    issolvable(start)
