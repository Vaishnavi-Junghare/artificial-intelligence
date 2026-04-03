from itertools import permutations

# Take user input
puzzle = input("Enter puzzle (Example: SEND + MORE = MONEY): ").upper()

# Replace = with ==
puzzle = puzzle.replace("=", "==")

# Get unique letters
letters = []
for ch in puzzle:
    if ch.isalpha() and ch not in letters:
        letters.append(ch)

# Check letter limit
if len(letters) > 10:
    print("Too many letters (max 10 allowed)")
else:
    # Get first letters (cannot be zero)
    words = puzzle.replace("==", "+").split("+")
    first_letters = []

    for word in words:
        word = word.strip()
        if word and word[0].isalpha():
            first_letters.append(word[0])

    # Try all digit combinations
    for perm in permutations(range(10), len(letters)):
        mapping = dict(zip(letters, perm))

        # Check leading zero condition
        valid = True
        for fl in first_letters:
            if mapping[fl] == 0:
                valid = False
                break

        if not valid:
            continue

        # Replace letters with digits
        equation = puzzle
        for letter in letters:
            equation = equation.replace(letter, str(mapping[letter]))

        # Check if equation is correct
        if eval(equation):
            print("\n✅ Solution Found:")
            print("Equation:", equation)
            print("Mapping:", mapping)
            break
    else:
        print("❌ No solution found.")