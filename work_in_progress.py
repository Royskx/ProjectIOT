import networkx as nx
import matplotlib.pyplot as plt
#import plotly.graph_objects as go
#from pyvis.network import Network
import dash
from dash import html
import dash_cytoscape as cyto


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


    def show_colorful(self):
        """Affichage coloré et lisible dans la console."""
        BOLD = "\033[1m"
        CYAN = "\033[96m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        RESET = "\033[0m"

        title = f"{BOLD}{CYAN}{'Graphe orienté' if self.directed else 'Graphe non orienté'}{RESET}"
        print("╭" + "─" * 60 + "╮")
        print(f"│ {title:<57} │")
        print("├" + "─" * 60 + "┤")

        for u, nbrs in self.adj.items():
            if not nbrs:
                print(f"│ {YELLOW}{u:<15}{RESET} │ (aucun voisin)")
                continue

            print(f"│ {YELLOW}{u:<15}{RESET} │ ", end="")
            rels = []
            for v, (tmin, tmax) in nbrs.items():
                arrow = "→" if self.directed else "—"
                rels.append(f"{v} {arrow} [{tmin}-{tmax}]")
            print(", ".join(rels))
        print("╰" + "─" * 60 + "╯")

        print(f"{GREEN}Sommets:{RESET} {len(self.nodes())} | {GREEN}Arêtes:{RESET} {len(self.edges())}\n")
    
    
    def draw(self, layout="spring"):
        """Dessine le graphe joliment, avec choix du layout."""
        G = nx.DiGraph() if self.directed else nx.Graph()

        for u, nbrs in self.adj.items():
            for v, (tmin, tmax) in nbrs.items():
                G.add_edge(u, v, label=f"{tmin}-{tmax}")

        # --- Choix du layout ---
        if layout == "spring":
            pos = nx.spring_layout(G, seed=42, k=0.8)  # layout "élastique"
        elif layout == "circular":
            pos = nx.circular_layout(G)
        elif layout == "planar":
            pos = nx.planar_layout(G)
        else:
            pos = nx.kamada_kawai_layout(G)

        # --- Création du graphe ---
        plt.figure(figsize=(7, 6))
        nx.draw_networkx_nodes(G, pos, node_size=2000, node_color="#5DADE2", edgecolors="black")
        nx.draw_networkx_labels(G, pos, font_color="white", font_weight="bold")

        nx.draw_networkx_edges(
            G, pos,
            arrowstyle="->" if self.directed else "-",
            arrowsize=20,
            width=2,
            edge_color="#34495E"
        )

        edge_labels = nx.get_edge_attributes(G, "label")
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="#1B2631", font_size=9)

        # --- Ajustement et titre ---
        plt.title("Graphe orienté" if self.directed else "Graphe non orienté", fontsize=14, fontweight="bold")
        plt.axis("off")
        plt.subplots_adjust(left=0.05, right=0.95, top=0.90, bottom=0.05)
        plt.show()
        
        
        ##################
    """
    def draw_plotly(self, filename="graphe_plotly.html"):
        G = nx.DiGraph() if self.directed else nx.Graph()
        for u, nbrs in self.adj.items():
            for v, (tmin, tmax) in nbrs.items():
                G.add_edge(u, v, label=f"{tmin}-{tmax}")

        pos = nx.spring_layout(G, seed=42)  # layout initial

        edge_x = []
        edge_y = []
        edge_labels = []
        for u, v, data in G.edges(data=True):
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]
            edge_labels.append(( (x0+x1)/2, (y0+y1)/2, data['label'] ))

        node_x = [pos[n][0] for n in G.nodes()]
        node_y = [pos[n][1] for n in G.nodes()]

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            marker=dict(size=40, color='#4e79a7', line=dict(width=2, color='black')),
            text=list(G.nodes()),
            textposition="bottom center",
            hoverinfo="text"
        )

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='#34495E'),
            hoverinfo='none',
            mode='lines'
        )

        edge_labels_trace = go.Scatter(
            x=[x for x, y, l in edge_labels],
            y=[y for x, y, l in edge_labels],
            text=[l for x, y, l in edge_labels],
            mode='text',
            textfont=dict(color="black", size=12),
            hoverinfo='none'
        )

        fig = go.Figure(data=[edge_trace, edge_labels_trace, node_trace],
                        layout=go.Layout(
                            title=f"{'Graphe orienté' if self.directed else 'Graphe non orienté'}",
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20,l=5,r=5,t=40),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                        ))

        fig.write_html(filename)
        print(f"Graphe interactif généré : {filename}")
        """
    def to_cytoscape_elements(self):
        """Convertit le graphe en format Cytoscape (nodes + edges)."""
        elements = []
        # Nodes
        for node in self.adj:
            elements.append({"data": {"id": node, "label": node}})
        # Edges
        for u, nbrs in self.adj.items():
            for v, (tmin, tmax) in nbrs.items():
                # Pour les graphes non orientés, éviter les doublons
                if not self.directed and any(e for e in elements if e.get("data", {}).get("source") == v and e.get("data", {}).get("target") == u):
                    continue
                elements.append({"data": {"source": u, "target": v, "label": f"{tmin}-{tmax}"}})
        return elements

    def draw_dash(self, port=8050):
        """Affiche le graphe dans le navigateur avec nœuds déplaçables."""

        app = dash.Dash(__name__)
        elements = self.to_cytoscape_elements()

        # ---- Ici on met le nouveau stylesheet pour rendre les labels plus visibles ----
        stylesheet = [
            # Nodes
            {'selector': 'node',
            'style': {
                'content': 'data(label)',
                'background-color': '#4e79a7',
                'color': 'white',
                'text-valign': 'center',
                'text-halign': 'center',
                'width': 50,
                'height': 50,
                'font-size': 14,
                'font-weight': 'bold'
            }},
            # Edges
            {'selector': 'edge',
            'style': {
                'label': 'data(label)',
                'curve-style': 'bezier',
                'target-arrow-shape': 'vee' if self.directed else 'none',
                'line-color': '#34495E',
                'target-arrow-color': '#34495E',
                'font-size': 16,               # taille plus grande
                'text-background-color': '#FFFFFF',  # fond blanc derrière label
                'text-background-opacity': 0.8,
                'text-margin-y': -10,          # label au-dessus de l’arête
                'color': '#FF5733'             # couleur du texte
            }}
        ]

        app.layout = html.Div([
            cyto.Cytoscape(
                id='cytoscape-graph',
                elements=elements,
                style={'width': '100%', 'height': '600px'},
                layout={'name': 'cose'},
                userZoomingEnabled=True,
                userPanningEnabled=True,
                boxSelectionEnabled=True,
                autoungrabify=False,
                stylesheet=stylesheet
            )
        ])

        print(f"Ouvrez navigateur à http://127.0.0.1:{port} pour voir le graphe interactif")
        app.run(debug=False, port=port)

    
        ################
def create_example_graph():
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

    return g


#################Partie 1 - Question 1######################

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
