import math

board = [[' ']*3 for _ in range(3)]

def show():
    for r in board:
        print(r[0], '|', r[1], '|', r[2])
        print("-"*9)

def win():
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != ' ':
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] != ' ':
            return board[0][i]

    if board[0][0] == board[1][1] == board[2][2] != ' ':
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != ' ':
        return board[0][2]

    if any(' ' in r for r in board):
        return None
    return "Tie"

def alphabeta(alpha, beta, maxp):
    w = win()
    if w == 'O':
        return 1
    if w == 'X':
        return -1
    if w == 'Tie':
        return 0

    if maxp:   # AI (O)
        v = -math.inf
        for i in range(3):
            for j in range(3):
                if board[i][j] == ' ':
                    board[i][j] = 'O'
                    v = max(v, alphabeta(alpha, beta, False))
                    board[i][j] = ' '
                    alpha = max(alpha, v)
                    if beta <= alpha:
                        return v
        return v
    else:      # Player (X)
        v = math.inf
        for i in range(3):
            for j in range(3):
                if board[i][j] == ' ':
                    board[i][j] = 'X'
                    v = min(v, alphabeta(alpha, beta, True))
                    board[i][j] = ' '
                    beta = min(beta, v)
                    if beta <= alpha:
                        return v
        return v

def best():
    move = (-1, -1)
    bestv = -math.inf
    for i in range(3):
        for j in range(3):
            if board[i][j] == ' ':
                board[i][j] = 'O'
                v = alphabeta(-math.inf, math.inf, False)
                board[i][j] = ' '
                if v > bestv:
                    bestv = v
                    move = (i, j)
    return move

# Game loop
while True:
    show()
    
    r = int(input("Row(1-3): ")) - 1
    c = int(input("Col(1-3): ")) - 1

    if board[r][c] == ' ':
        board[r][c] = 'X'
    else:
        print("Invalid move!")
        continue

    if win():
        break

    i, j = best()
    board[i][j] = 'O'
    print("AI move:", i+1, j+1)

    if win():
        break

show()
result = win()
if result == "Tie":
    print("It's a Tie!")
else:
    print(result, "Wins!")