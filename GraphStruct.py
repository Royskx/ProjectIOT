import networkx as nx
import matplotlib.pyplot as plt
import dash
from dash import html
import dash_cytoscape as cyto
import numpy as np
import scipy.stats

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
        """Ajoute une arête u->v avec deux poids (temps_min, temps_max)."""
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
    
    def noisy_edge_mean_gauss(self, tmin, tmax, noise_scale=1.0, n_samples=1000):
        """
        Utilise Beta pour créer des gaussiennes décentrées de façon contrôlée
        """
        # Choisir aléatoirement un "profil" de trafic
        profile = np.random.choice(['fluide', 'normal', 'dense'])
        
        if profile == 'fluide':
            # Trafic fluide → pic vers tmin
            alpha, beta = 2, 5
        elif profile == 'dense':
            # Trafic dense → pic vers tmax
            alpha, beta = 5, 2
        else:
            # Normal → pic au centre
            alpha, beta = 2, 2

        # Générer la position du centre
        beta_sample = np.random.beta(alpha, beta)
        mu = tmin + beta_sample * (tmax - tmin)
        
        # Écart-type
        std = (tmax - tmin) / (5 + noise_scale)
        
        # Générer échantillons
        samples = np.random.normal(mu, std, n_samples)
        samples = samples[(samples >= tmin) & (samples <= tmax)]
        
        if len(samples) == 0:
            return mu
        
        return np.mean(samples)

    def noisy_edge_mean_beta(self, tmin, tmax, n_samples=1000, 
                    congestion_speed=0.1, liberation_every=100, liberation_force=0.3):
    
        """
        Simule une route i.i.d avec du trafic qui évolue dans le temps.
        
        Imagine : tu observes cette route pendant 1000 moments différents.
        Le trafic s'accumule progressivement, puis se libère de temps en temps.
        
        Paramètres:
        -----------
        tmin, tmax : temps min et max du trajet (en minutes par exemple)
        n_samples : combien de "moments" on observe
        congestion_speed : vitesse d'accumulation du trafic (0.0 = aucune, 1.0 = rapide)
        liberation_every : tous les combien de moments la route se libère
        liberation_force : intensité de la libération (0.0 = aucune, 1.0 = complète)
        """
    
        initial_state = np.random.choice(['fluide', 'normal', 'dense'])
        
        if initial_state == 'fluide':
            alpha_start, beta_start = 2, 5
            alpha_limit, beta_limit = 5, 2
        elif initial_state == 'dense':
            alpha_start, beta_start = 5, 2
            alpha_limit, beta_limit = 2, 5
        else:
            alpha_start, beta_start = 2, 2
            alpha_limit, beta_limit = 3, 3
        
        observed_times = []
        alpha = alpha_start
        beta = beta_start
        
        for moment in range(n_samples):     
            beta_sample = np.random.beta(alpha, beta)
            travel_time = tmin + beta_sample * (tmax - tmin)
            observed_times.append(travel_time)
            
            if moment % liberation_every == 0:
                alpha += np.abs(alpha_start - alpha) * liberation_force
                beta += np.abs(beta_start - beta) * liberation_force
            
            progress = moment / n_samples
            alpha += (alpha_limit - alpha) * congestion_speed * 0.01
            beta += (beta_limit - beta) * congestion_speed * 0.01
            
            alpha = np.clip(alpha, 0.5, 10)
            beta = np.clip(beta, 0.5, 10)
        
        valid_times = [t for t in observed_times if tmin <= t <= tmax]
        
        if len(valid_times) == 0:
            return (tmin + tmax) / 2
        
        return np.mean(valid_times)

    def make_converge(self, beta = False, n_samples=1000):
        """
        Pour chaque arête, crée une gaussienne bruitée et estime la moyenne empirique,
        puis crée un nouveau graphe avec ces valeurs.
        """
        g = SimpleGraph(directed=self.directed)
        noise_scale = np.random.uniform(0, 0.5)

        for u, v, tmin, tmax in self.edges():
            if beta:
                mean_estimee = self.noisy_edge_mean_beta(tmin, tmax, n_samples)
            else:
                mean_estimee = self.noisy_edge_mean_gauss(tmin, tmax, noise_scale, n_samples)
            g.add_node(u)
            g.add_node(v)
            g.add_edge(u, v, round(mean_estimee,2), round(mean_estimee,2))
        return g
            

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




"""
Unused Codes

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

    def noisy_edge_mean(self, tmin, tmax, noise_scale, n_samples=1000):
        mu = np.mean([tmin, tmax])
        std = (tmax - tmin) / 6
        # Ajout de bruit à la moyenne
        mu_bruite = mu + np.random.normal(0, noise_scale * std)
        # Générer des échantillons de la gaussienne
        samples = np.random.normal(mu_bruite, std, n_samples)
        samples = samples[(samples >= tmin) & (samples <= tmax)]
        # Estimer la nouvelle moyenne
        if len(samples) == 0:
            return np.clip(mu_bruite, tmin, tmax)
        return np.mean(samples)


    def draw(self, layout="spring"):
        Dessine le graphe joliment, avec choix du layout.
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
    
"""


"""
    def to_cytoscape_elements(self):
        Convertit le graphe en format Cytoscape (nodes + edges).
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

    def draw_dash(self, port=8050, path=None, heuristic_name=None, path_length=None):
        app = dash.Dash(__name__)
        elements = self.to_cytoscape_elements()

        # Repérer les arêtes et nœuds du chemin
        path_edges = set()
        path_nodes = set(path) if path else set()
        if path and len(path) > 1:
            for i in range(len(path) - 1):
                path_edges.add((str(path[i]), str(path[i+1])))
                if not self.directed:
                    path_edges.add((str(path[i+1]), str(path[i])))

        # Stylesheet avec coloration du chemin
        stylesheet = [
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
            {'selector': 'edge',
            'style': {
                'label': 'data(label)',
                'curve-style': 'bezier',
                'target-arrow-shape': 'vee' if self.directed else 'none',
                'line-color': '#34495E',
                'target-arrow-color': '#34495E',
                'font-size': 16,
                'text-background-color': '#FFFFFF',
                'text-background-opacity': 0.8,
                'text-margin-y': -10,
                'color': '#FF5733'
            }},
        ]

        for node in path_nodes:
            stylesheet.append({
                'selector': f'node[id = "{node}"]',
                'style': {
                    'background-color': '#27ae60',
                    'border-width': 4,
                    'border-color': '#145a32'
                }
            })

        for u, v in path_edges:
            stylesheet.append({
                'selector': f'edge[source = "{u}"][target = "{v}"]',
                'style': {
                    'line-color': '#e040fb',
                    'target-arrow-color': '#e040fb',
                    'width': 5
                }
            })

        # Affichage du nom de l'heuristique et de la taille du chemin
        header = []
        if heuristic_name:
            header.append(html.H3(f"Heuristique : {heuristic_name}", style={"color": "#e67e22"}))
        if path_length is not None:
            header.append(html.H4(f"Taille du chemin : {path_length}", style={"color": "#27ae60"}))

        app.layout = html.Div(
            header + [
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
            ]
        )

        print(f"\nOuvrez navigateur à http://127.0.0.1:{port} pour voir le graphe interactif")
        app.run(debug=False, port=port)
"""