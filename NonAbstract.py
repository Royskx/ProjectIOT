#################Partie 1 - Question 2######################


"""def worst_case_dij(graph, start, end):
    non_visited = set(graph.nodes())
    distances = {node: float('-inf') for node in graph.nodes()}
    distances[start] = 0
    precedent = {node: None for node in graph.nodes()}

    while non_visited:
        current = max(non_visited, key=lambda s: distances[s])
        if distances[current] == float('-inf'):
            break
        non_visited.remove(current)

        if current == end:
            break

        for neighbor, (_, worst_time) in graph.neighbors(current).items():
            if neighbor in non_visited:
                new_dist = distances[current] + worst_time
                if new_dist > distances[neighbor]:
                    distances[neighbor] = new_dist
                    precedent[neighbor] = current

    route = []
    current = end
    while current is not None:
        route.insert(0, current)
        current = precedent[current]

    if distances[end] == float('-inf'):
        return None, float('-inf')

    return route, distances#[end]


print("Worst case de 1 à 11 :", worst_case_dij(g, 1, 11))"""


def worst_case(graph, start, end):
    visited = set()
    topo_order = []

    def dfs(node):
        visited.add(node)
        for neighbor in graph.neighbors(node):
            if neighbor not in visited:
                dfs(neighbor)
        topo_order.append(node)

    for node in graph.nodes():
        if node not in visited:
            dfs(node)
    topo_order.reverse()

    distances = {node: float('-inf') for node in graph.nodes()}
    distances[start] = 0
    precedent = {node: None for node in graph.nodes()}

    for u in topo_order:
        for v, (_, worst_time) in graph.neighbors(u).items():
            if distances[u] + worst_time > distances[v]:
                distances[v] = distances[u] + worst_time
                precedent[v] = u

    path = []
    current = end
    while current is not None:
        path.insert(0, current)
        current = precedent[current]

    if not path or path[0] != start:
        return None, float('-inf')  # pas de chemin

    return path, distances[end]




#################Partie 2 - Question 1-4######################
def most_stable_path(graph, start, end):
    visited = set()
    topo_order = []

    def dfs(node):
        visited.add(node)
        for neighbor in graph.neighbors(node):
            if neighbor not in visited:
                dfs(neighbor)
        topo_order.append(node)

    for node in graph.nodes():
        if node not in visited:
            dfs(node)
    topo_order.reverse()

    distances = {node: float('inf') for node in graph.nodes()}
    distances[start] = 0
    precedent = {node: None for node in graph.nodes()}

    for u in topo_order:
        for v, (tmin, tmax) in graph.neighbors(u).items():
            marge = tmax - tmin
            if distances[u] + marge < distances[v]:
                distances[v] = distances[u] + marge
                precedent[v] = u

    path = []
    current = end
    while current is not None:
        path.insert(0, current)
        current = precedent[current]

    if not path or path[0] != start:
        return None, float('inf')  # Pas de chemin trouvé

    return path, distances[end]

