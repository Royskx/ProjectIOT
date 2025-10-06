class SimpleGraph:
    """
    Graphe orienté ou non, avec arêtes contenant deux poids : temps_min et temps_max.
    Représentation : adj[u][v] = (temps_min, temps_max)
    """
    def __init__(self, directed=False):
        self.directed = directed
        self.adj = {}  # {node: {neighbor: (temps_min, temps_max)}}

    def add_node(self, v):
        if v not in self.adj:
            self.adj[v] = {}

    def add_edge(self, u, v, temps_min, temps_max):
        """Ajoute une arête u→v avec deux poids (temps_min, temps_max)."""
        self.add_node(u)
        self.add_node(v)
        self.adj[u][v] = (temps_min, temps_max)
        if not self.directed:
            self.adj[v][u] = (temps_min, temps_max)

    def remove_edge(self, u, v):
        if u in self.adj and v in self.adj[u]:
            del self.adj[u][v]
        if not self.directed and v in self.adj and u in self.adj[v]:
            del self.adj[v][u]

    def remove_node(self, v):
        if v not in self.adj:
            return
        for nbrs in self.adj.values():
            nbrs.pop(v, None)
        del self.adj[v]

    def neighbors(self, v):
        return dict(self.adj.get(v, {}))

    def nodes(self):
        return list(self.adj.keys())

    def edges(self):
        edges = []
        seen = set()
        for u, nbrs in self.adj.items():
            for v, (tmin, tmax) in nbrs.items():
                if self.directed or (v, u) not in seen:
                    edges.append((u, v, tmin, tmax))
                    seen.add((u, v))
        return edges

    def has_node(self, v):
        return v in self.adj

    def has_edge(self, u, v):
        return u in self.adj and v in self.adj[u]

    def degree(self, v):
        return len(self.adj.get(v, {}))

    def show(self):
        """Affiche le graphe dans la console."""
        print(f"{'Graphe orienté' if self.directed else 'Graphe non orienté'} :")
        for u, nbrs in self.adj.items():
            if self.directed:
                arrows = ", ".join(
                    f"→ {v} ({tmin}-{tmax})" for v, (tmin, tmax) in nbrs.items()
                )
            else:
                arrows = ", ".join(
                    f"{v} ({tmin}-{tmax})" for v, (tmin, tmax) in nbrs.items()
                )
            print(f"  {u}: {arrows}")
        print(f"→ {len(self.nodes())} sommets, {len(self.edges())} arêtes\n")

g = SimpleGraph(directed=True)

for n in range(1, 12):
    g.add_node(n)
    
g.add_edge(1, 2, 3, 7)
g.add_edge(1, 3, 4, 6)
g.add_edge(1, 4, 3, 8)
g.add_edge(2, 5, 2, 5)
g.add_edge(3, 5, 5, 8)
g.add_edge(3, 6, 4, 6)
g.add_edge(4, 6, 7, 10)
g.add_edge(4, 7, 3, 8)
g.add_edge(5, 8, 4, 9)
g.add_edge(6, 8, 2, 4)
g.add_edge(6, 9, 5, 6)
g.add_edge(7, 9, 2, 4)
g.add_edge(7, 10, 4, 7)
g.add_edge(8, 11, 3, 7)
g.add_edge(9, 11, 3, 6)
g.add_edge(10, 11, 3, 4)

g.show()


def count_routes(graph, start, end):
    """Compte le nombre de routes de start à end."""
    def dfs(node, stops):
        if node == end and stops > 0:
            return 1
        count = 0
        for neighbor in graph.neighbors(node):
            count += dfs(neighbor, stops + 1)
        return count
    return dfs(start, 0)

print("Nombre de routes de 1 à 11 :", count_routes(g, 1, 11))
