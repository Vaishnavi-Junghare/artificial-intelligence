from collections import deque

def solve_water_jug(cap_x, cap_y, target):
    queue = deque([((0, 0), [])])
    visited = set([(0, 0)])

    while queue:
        (x, y), path = queue.popleft()

        # Check goal
        if x == target or y == target:
            return path + [(x, y)]

        # All possible moves
        rules = [
            (cap_x, y, "Fill Jug X"),
            (x, cap_y, "Fill Jug Y"),
            (0, y, "Empty Jug X"),
            (x, 0, "Empty Jug Y"),
            (x - min(x, cap_y - y), y + min(x, cap_y - y), "Pour X -> Y"),
            (x + min(y, cap_x - x), y - min(y, cap_x - x), "Pour Y -> X")
        ]

        for next_x, next_y, action in rules:
            if (next_x, next_y) not in visited:
                visited.add((next_x, next_y))
                queue.append(((next_x, next_y), path + [(x, y, action)]))

    return None


# User input
m = int(input("Enter Jug 1 Size: "))
n = int(input("Enter Jug 2 Size: "))
d = int(input("Enter Target Jug Size: "))

solution = solve_water_jug(m, n, d)

# Output
if solution:
    print("\nSteps to reach goal:")
    for step in solution[:-1]:
        print(f"State {(step[0], step[1])} -> Action: {step[2]}")
    print(f"Final State: {solution[-1]}")
else:
    print("No solution possible.")