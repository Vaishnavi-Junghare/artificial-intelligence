board = [" "] * 9

p1 = input("Player 1 symbol: ")
p2 = input("Player 2 symbol: ")

def show():
    print(board[0], "|", board[1], "|", board[2])
    print("--+---+--")
    print(board[3], "|", board[4], "|", board[5])
    print("--+---+--")
    print(board[6], "|", board[7], "|", board[8])

wins = [
    (0,1,2), (3,4,5), (6,7,8),
    (0,3,6), (1,4,7), (2,5,8),
    (0,4,8), (2,4,6)
]

player = p1

for _ in range(9):
    show()
    
    move = int(input(f"{player} move (1-9): ")) - 1
    
    # Check if move is valid
    if board[move] != " ":
        print("Invalid move! Try again.")
        continue
    
    board[move] = player

    # Check win
    for a, b, c in wins:
        if board[a] == board[b] == board[c] == player:
            show()
            print(player, "wins!")
            quit()

    # Switch player
    player = p2 if player == p1 else p1

show()
print("Draw!")