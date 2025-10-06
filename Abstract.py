def best_path(graph, start, end, cost_func, maximize=False):
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

    if maximize:
        distances = {node: float('-inf') for node in graph.nodes()}
    else:
        distances = {node: float('inf') for node in graph.nodes()}
    distances[start] = 0
    precedent = {node: None for node in graph.nodes()}

    for u in topo_order:
        for v, (tmin, tmax) in graph.neighbors(u).items():
            cost = cost_func(u, v, tmin, tmax)
            if maximize:
                if distances[u] + cost > distances[v]:
                    distances[v] = distances[u] + cost
                    precedent[v] = u
            else:
                if distances[u] + cost < distances[v]:
                    distances[v] = distances[u] + cost
                    precedent[v] = u

    path = []
    current = end
    while current is not None:
        path.insert(0, current)
        current = precedent[current]

    if not path or path[0] != start:
        return None, float('inf') if not maximize else float('-inf')

    return path, distances[end]


def cost_min(u, v, tmin, tmax):
    return tmin

def cost_max(u, v, tmin, tmax):
    return tmax

def cost_marge(u, v, tmin, tmax):
    return tmax - tmin
