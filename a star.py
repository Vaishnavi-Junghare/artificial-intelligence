# Graph representation
graph = {
    'A': [('B', 1), ('C', 4)],
    'B': [('D', 5), ('E', 1)],
    'C': [('F', 3)],
    'D': [],
    'E': [('G', 2)],
    'F': [('G', 1)],
    'G': []
}

# Heuristic values (estimated distance to goal 'G')
heuristic = {
    'A': 7,
    'B': 6,
    'C': 5,
    'D': 3,
    'E': 1,
    'F': 2,
    'G': 0
}

# A* Search Algorithm
def a_star(graph, heuristic, start, goal):
    open_list = [start]      # Nodes to be evaluated
    closed_list = []         # Nodes already evaluated

    g_cost = {start: 0}      # Cost from start node
    parent = {start: None}   # To store path

    while open_list:
        # Find node with lowest f = g + h
        current = open_list[0]
        for node in open_list:
            if g_cost[node] + heuristic[node] < g_cost[current] + heuristic[current]:
                current = node

        open_list.remove(current)
        closed_list.append(current)

        # If goal reached
        if current == goal:
            path = []
            while current is not None:
                path.append(current)
                current = parent[current]
            return path[::-1], g_cost[goal]

        # Check neighbors
        for neighbor, cost in graph[current]:
            if neighbor in closed_list:
                continue

            tentative_g = g_cost[current] + cost

            if neighbor not in open_list:
                open_list.append(neighbor)
            elif tentative_g >= g_cost.get(neighbor, float('inf')):
                continue

            parent[neighbor] = current
            g_cost[neighbor] = tentative_g

    return None, float('inf')


# Run A* algorithm
path, cost = a_star(graph, heuristic, 'A', 'G')

print("Shortest Path:", path)
print("Shortest Path Cost:", cost)