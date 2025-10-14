#to pick a random move for the "human"
import random
#to measure execution time of the algorithms
import time

# ------------------ Board Utilities ------------------
def print_board(board):
    for row in board:
        print("|".join(row))
        print("-"*5)

#Checks if there are any empty spaces left on the board.
# Returns True if at least one cell is empty.
def is_moves_left(board):
    return any(cell == ' ' for row in board for cell in row)

#Evaluates any player has won the Tic-Tac-Toe game.
# Returns:10 → Computer ('X') wins.-10 → Human ('O') wins.0 → No one has won yet.
def evaluate(board):
    # Check rows and columns
    for i in range(3):
        #checks if all 3 cells in row i are equal and not empty.
        if board[i][0] == board[i][1] == board[i][2] != ' ':
            return 10 if board[i][0] == 'X' else -10
        if board[0][i] == board[1][i] == board[2][i] != ' ':
            return 10 if board[0][i] == 'X' else -10
        
    # Check diagonals
    #main diagonal (top-left to bottom-right).
    if board[0][0] == board[1][1] == board[2][2] != ' ':
        return 10 if board[0][0] == 'X' else -10
    #anti-diagonal (top-right to bottom-left).
    if board[0][2] == board[1][1] == board[2][0] != ' ':
        return 10 if board[0][2] == 'X' else -10
    #no winner- draw case or still running.
    return 0

# ------------------ Minimax Algorithm ------------------
#to track how many nodes the algorithm evaluates.
minimax_nodes = 0
#is_max → True if it’s the computer’s turn, False for the human.
##Computer tries all possible moves and chooses the one that maximizes its chances of winning.
def minimax(board, is_max):
    global minimax_nodes
    minimax_nodes += 1

    score = evaluate(board)
    #Base case: if the game is over, return the score.If the board is full and no winner → draw → return 0.
    if score == 10 or score == -10:
        return score
    if not is_moves_left(board):
        return 0
    
#Try all empty cells.Place 'X' in that cell and recursively call minimax for human.
# Keep track of the maximum score (best move for computer).
    if is_max:
        best = -1000
        for i in range(3):
            for j in range(3):
                if board[i][j] == ' ':
                    board[i][j] = 'X'
                    best = max(best, minimax(board, False))
                    board[i][j] = ' '#backtracking
        return best
    #For human’s turn:Place 'O' and recursively call minimax for computer.
    # Keep track of the minimum score (worst-case for computer).
    #Human is assumed to play perfectly and will always try to minimize the computer’s score.
    else:
        best = 1000
        for i in range(3):
            for j in range(3):
                if board[i][j] == ' ':
                    board[i][j] = 'O'
                    best = min(best, minimax(board, True))
                    board[i][j] = ' '
        return best
    
#Iterates all possible moves for the computer.Calls minimax to get the value of that move.
# Returns the move with the highest score.
def find_best_move(board):
    best_val = -1000
    best_move = (-1, -1)
    for i in range(3):
        for j in range(3):
            if board[i][j] == ' ':
                board[i][j] = 'X'
                move_val = minimax(board, False)
                board[i][j] = ' '
                if move_val > best_val:
                    best_val = move_val
                    best_move = (i, j)
    return best_move

# ------------------ Alpha-Beta Pruning ------------------
ab_nodes = 0
#alpha-maximiser
#beta-minimiser
def minimax_ab(board, alpha, beta, is_max):
    global ab_nodes
    ab_nodes += 1

    score = evaluate(board)
    if score == 10 or score == -10:
        return score
    if not is_moves_left(board):
        return 0

    if is_max:
        best = -1000
        for i in range(3):
            for j in range(3):
                if board[i][j] == ' ':
                    board[i][j] = 'X'
                    best = max(best, minimax_ab(board, alpha, beta, False))
                    board[i][j] = ' '
                    alpha = max(alpha, best)
                    #If beta <= alpha → prune the remaining branches (skip them).
                    if beta <= alpha:
                        break
        return best
    else:
        best = 1000
        for i in range(3):
            for j in range(3):
                if board[i][j] == ' ':
                    board[i][j] = 'O'
                    best = min(best, minimax_ab(board, alpha, beta, True))
                    board[i][j] = ' '
                    beta = min(beta, best)
                    if beta <= alpha:
                        break
        return best

def find_best_move_ab(board):
    best_val = -1000
    best_move = (-1, -1)
    for i in range(3):
        for j in range(3):
            if board[i][j] == ' ':
                board[i][j] = 'X'
                move_val = minimax_ab(board, -1000, 1000, False)
                board[i][j] = ' '
                if move_val > best_val:
                    best_val = move_val
                    best_move = (i, j)
    return best_move

# ------------------ Game Loop ------------------
#Creates an empty board.
#use_alpha_beta → Determines whether to use Minimax or Alpha-Beta.
def play_game(use_alpha_beta=True):
    global minimax_nodes, ab_nodes
    board = [[' ']*3 for _ in range(3)]
    print_board(board)

    for turn in range(9):
        if turn % 2 == 0:
            # Computer Move
            start = time.time()
            if use_alpha_beta:
                best_move = find_best_move_ab(board)
            else:
                best_move = find_best_move(board)
            end = time.time()
            board[best_move[0]][best_move[1]] = 'X'
            print("Computer plays X:")
            print_board(board)
            print(f"Time taken: {end-start:.4f} seconds")
        else:
            # Human Move (manual input)
            #keep asking for input until the user gives a valid move.
            while True:
                try:
                    #splits that into a list of two strings → ['1', '2']   
                    # map(int, ...) converts them to integers
                    r, c = map(int, input("Enter your move (row and column 0-2 separated by space): ").split())
                   
                    #Row and column numbers are between 0 and 2 (since it’s a 3×3 board).
                    # The selected cell is empty (' ').
                    if 0 <= r <= 2 and 0 <= c <= 2 and board[r][c] == ' ':
                        board[r][c] = 'O'
                        #Then we break the loop to continue the game.
                        break
                    else:
                        #if error we print an error and re ask.
                        print("Invalid move! Try again.")
                except ValueError:
                    print("Please enter two integers between 0 and 2.")
            print(f"Human plays O at {r},{c}")
            print_board(board)

        score = evaluate(board)
        if score == 10:
            print("Computer wins!")
            break
        elif score == -10:
            print("Human wins!")
            break
    else:
        print("Game Draw (-1)")

# ------------------ Run and Compare ------------------
print("===== Minimax vs Alpha-Beta Comparison =====")
minimax_nodes = 0
ab_nodes = 0

# Minimax Test
print("\nPlaying with Minimax:")
start_time = time.time()
play_game(use_alpha_beta=False)
minimax_time = time.time() - start_time
print(f"Nodes visited (Minimax): {minimax_nodes}")
print(f"Execution time (Minimax): {minimax_time:.4f} sec")

# Alpha-Beta Test
print("\nPlaying with Alpha-Beta Pruning:")
start_time = time.time()
play_game(use_alpha_beta=True)
ab_time = time.time() - start_time
print(f"Nodes visited (Alpha-Beta): {ab_nodes}")
print(f"Execution time (Alpha-Beta): {ab_time:.4f} sec")


#Create a 3×3 board.Evaluate board after every move.Minimax explores all possible moves recursively.
#Alpha-Beta prunes unnecessary branches → fewer nodes visited.
#Compare nodes visited and execution time → see efficiency gains.

# ------------------ Summary Section ------------------
improvement_nodes = ((minimax_nodes - ab_nodes) / minimax_nodes * 100) if minimax_nodes else 0
improvement_time = ((minimax_time - ab_time) / minimax_time * 100) if minimax_time else 0

print("\n===== SUMMARY")
print(f"NODES (Space Used):")
print(f"   Minimax expanded {minimax_nodes} nodes")
print(f"   Alpha–Beta expanded {ab_nodes} nodes")
print(f"   Space reduction: {improvement_nodes:.2f}% fewer nodes expanded\n")

print(f"EXECUTION TIME (Speed):")
print(f"   Minimax took {minimax_time:.4f} seconds")
print(f"   Alpha–Beta took {ab_time:.4f} seconds")
print(f"   Speed improvement: {improvement_time:.2f}% faster\n")

print("=LAST QUESTION O/P")
print("- Alpha–Beta pruning reduces both time and space requirements drastically.")
print("- It achieves the same optimal result as Minimax but explores fewer nodes.")
print("- The best-case time complexity improves from O(b^d) to O(b^(d/2)).")
#exploring the most promising nodes first.
print("- Node reordering (evaluating promising moves first) can further improve pruning efficiency.")
