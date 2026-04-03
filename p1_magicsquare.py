n = int(input("Enter an odd number: "))

# Check if number is odd
if n % 2 == 0:
    print("Please enter an ODD number only.")
else:
    # Create empty matrix
    magic = [[0] * n for _ in range(n)]

    # Starting position
    i = n // 2
    j = n - 1

    # Fill the magic square
    for num in range(1, n * n + 1):

        if i == -1 and j == n:   # condition 1
            i = 0
            j = n - 2
        else:
            if i < 0:            # row goes out
                i = n - 1
            if j == n:           # column goes out
                j = 0

        if magic[i][j] != 0:     # cell already filled
            i += 1
            j -= 2
            continue
        else:
            magic[i][j] = num

        i -= 1
        j += 1

    # Print Magic Square
    print("\nMagic Square Matrix:")
    for row in magic:
        for val in row:
            print(val, end=" ")
        print()

    # Magic Sum
    magic_sum = n * (n * n + 1) // 2
    print("\nMagic Sum:", magic_sum)