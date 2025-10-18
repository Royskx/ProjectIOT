import dash
from dash import html, dcc, Input, Output, State
import dash_cytoscape as cyto
from Abstract import best_path, cost_min, cost_max, cost_marge

def show_colorful(g):
    """Affichage coloré et lisible dans la console."""
    BOLD = "\033[1m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"

    title = f"{BOLD}{CYAN}{'Graphe orienté' if g.directed else 'Graphe non orienté'}{RESET}"
    print("╭" + "─" * 60 + "╮")
    print(f"│ {title:<57} │")
    print("├" + "─" * 60 + "┤")

    for u, nbrs in g.adj.items():
        if not nbrs:
            print(f"│ {YELLOW}{u:<15}{RESET} │ (aucun voisin)")
            continue

        print(f"│ {YELLOW}{u:<15}{RESET} │ ", end="")
        rels = []
        for v, (tmin, tmax) in nbrs.items():
            arrow = "→" if g.directed else "—"
            rels.append(f"{v} {arrow} [{tmin}-{tmax}]")
        print(", ".join(rels))
    print("╰" + "─" * 60 + "╯")

    print(f"{GREEN}Sommets:{RESET} {len(g.nodes())} | {GREEN}Arêtes:{RESET} {len(g.edges())}\n")


def create_interactive_dashboard(graph, start, end, port=8050):
    """
    Dashboard interactif avec boutons pour toutes les heuristiques.
    Plus besoin de Ctrl+C et relancer !
    """
    
    app = dash.Dash(__name__)
    
    # Calculer tous les chemins à l'avance
    heuristics = {}
    
    try:
        path, val = best_path(graph, start, end, cost_min, maximize=False)
        heuristics['Optimistic'] = {
            'name': '🌟 Optimiste (temps min)',
            'path': path,
            'value': val,
            'description': f'Temps minimum total: {val:.2f} min'
        }
    except:
        heuristics['optimistic'] = None
    
    try:
        path, val = best_path(graph, start, end, cost_max, maximize=False)
        heuristics['prudent'] = {
            'name': '🛡️ Prudent (temps max)',
            'path': path,
            'value': val,
            'description': f'Temps maximum total: {val:.2f} min'
        }
    except:
        heuristics['prudent'] = None
    
    try:
        path, val = best_path(graph, start, end, cost_marge, maximize=False)
        heuristics['stable'] = {
            'name': '⚖️ Stable (marge min)',
            'path': path,
            'value': val,
            'description': f'Marge de fluctuation: {val:.2f} min'
        }
    except:
        heuristics['stable'] = None
    
    try:
        path, val = best_path(graph, start, end, cost_marge, maximize=True)
        heuristics['Least stable'] = {
            'name': '⚖️ Least Stable (marge max)',
            'path': path,
            'value': val,
            'description': f'Marge de fluctuation: {val:.2f} min'
        }
    except:
        heuristics['Least stable'] = None
    
    try:
        path, val = best_path(graph, start, end, cost_max, maximize=True)
        heuristics['worst'] = {
            'name': '💀 Pire cas (max-max)',
            'path': path,
            'value': val,
            'description': f'Temps maximum absolu: {val:.2f} min'
        }
    except:
        heuristics['worst'] = None
    
    # Graphe moyen si disponible
    g_mean = None
    try:
        g_mean = graph.make_converge(n_samples=1000)
        path, val = best_path(g_mean, start, end, cost_min, maximize=False)
        heuristics['gaussian'] = {
            'name': '📊 Gaussian Distribution',
            'path': path,
            'value': val,
            'description': f'Temps moyen convergé: {val:.2f} min',
            'graph': g_mean  # Garder le graphe modifié
        }
    except:
        heuristics['gaussian'] = None
        
    try:
        g_mean = graph.make_converge(beta = True, n_samples=1000)
        path, val = best_path(g_mean, start, end, cost_min, maximize=False)
        heuristics['beta'] = {
            'name': '📊 Beta Distribution',
            'path': path,
            'value': val,
            'description': f'Temps moyen convergé: {val:.2f} min',
            'graph': g_mean  # Garder le graphe modifié
        }
    except:
        heuristics['beta'] = None
        
    def get_cytoscape_elements(selected_heuristic):
        """Génère les éléments Cytoscape avec le chemin coloré"""
        elements = []
        
        # Choisir le bon graphe selon l'heuristique
        current_graph = graph
        if selected_heuristic == 'gaussian' and heuristics.get('gaussian'):
            current_graph = heuristics['gaussian'].get('graph', graph)
        
        if selected_heuristic == 'beat' and heuristics.get('beta'):
            current_graph = heuristics['beta'].get('graph', graph)
        # Nodes
        for node in current_graph.adj:
            elements.append({"data": {"id": str(node), "label": str(node)}})
        
        # Path info
        path = None
        if selected_heuristic and heuristics.get(selected_heuristic):
            path = heuristics[selected_heuristic]['path']
        
        path_edges = set()
        path_nodes = set(map(str, path)) if path else set()
        
        if path and len(path) > 1:
            for i in range(len(path) - 1):
                path_edges.add((str(path[i]), str(path[i+1])))
                if not current_graph.directed:
                    path_edges.add((str(path[i+1]), str(path[i])))
        
        # Edges (utiliser current_graph pour les labels)
        for u, nbrs in current_graph.adj.items():
            for v, (tmin, tmax) in nbrs.items():
                if not current_graph.directed and any(e for e in elements if 
                    e.get("data", {}).get("source") == str(v) and 
                    e.get("data", {}).get("target") == str(u)):
                    continue
                
                # Pour Gaussian, afficher la moyenne estimée
                if selected_heuristic == 'gaussian' and abs(tmin - tmax) < 0.01:
                    label = f"{tmin:.2f}"
                else:
                    label = f"{tmin}-{tmax}"
                
                edge_data = {
                    "data": {
                        "source": str(u), 
                        "target": str(v), 
                        "label": label
                    }
                }
                elements.append(edge_data)
        # Stylesheet
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
                'target-arrow-shape': 'vee' if current_graph.directed else 'none',
                'line-color': '#34495E',
                'target-arrow-color': '#34495E',
                'font-size': 11,
                'text-background-color': '#FFFFFF',
                'text-background-opacity': 0.8,
                'text-margin-y': -10,
                'color': '#2C3E50',
                'width': 2
            }},
        ]
        
        # Style pour les nœuds du chemin
        for node in path_nodes:
            stylesheet.append({
                'selector': f'node[id = "{node}"]',
                'style': {
                    'background-color': '#27ae60',
                    'border-width': 4,
                    'border-color': '#145a32'
                }
            })
        
        # Style pour les arêtes du chemin
        for u, v in path_edges:
            stylesheet.append({
                'selector': f'edge[source = "{u}"][target = "{v}"]',
                'style': {
                    'line-color': '#e040fb',
                    'target-arrow-color': '#e040fb',
                    'width': 5,
                    'z-index': 999
                }
            })
        
        return elements, stylesheet
    
    # Layout de l'app
    app.layout = html.Div([
        html.Div([
            html.H1("🗺️ Analyse des Chemins Robustes", 
                   style={'textAlign': 'center', 'color': '#2C3E50', 'marginBottom': '10px'}),
            html.H3(f"De {start} à {end}", 
                   style={'textAlign': 'center', 'color': '#7F8C8D', 'marginTop': '0px'}),
        ], style={'backgroundColor': '#ECF0F1', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '20px'}),
        
        # Boutons pour les heuristiques
        html.Div([
            html.H4("Choisissez une heuristique:", style={'marginBottom': '15px', 'color': '#34495E'}),
            html.Div([
                html.Button(
                    h['name'],
                    id={'type': 'heuristic-btn', 'index': key},
                    n_clicks=0,
                    style={
                        'margin': '5px',
                        'padding': '12px 24px',
                        'fontSize': '16px',
                        'borderRadius': '8px',
                        'border': '2px solid #3498db',
                        'backgroundColor': '#3498db',
                        'color': 'white',
                        'cursor': 'pointer',
                        'fontWeight': 'bold',
                        'transition': 'all 0.3s'
                    }
                ) for key, h in heuristics.items() if h is not None
            ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'center'})
        ], style={'backgroundColor': '#FFFFFF', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '20px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
        
        # Zone d'information
        html.Div(id='info-panel', style={
            'backgroundColor': '#FFFFFF',
            'padding': '20px',
            'borderRadius': '10px',
            'marginBottom': '20px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            'minHeight': '80px'
        }),
        
        # Graphe
        html.Div([
            cyto.Cytoscape(
                id='cytoscape-graph',
                elements=[],
                style={'width': '100%', 'height': '600px'},
                layout={'name': 'cose', 'animate': True, 'animationDuration': 500},
                userZoomingEnabled=True,
                userPanningEnabled=True,
                boxSelectionEnabled=False,
                autoungrabify=False,
                stylesheet=[]
            )
        ], style={'backgroundColor': '#FFFFFF', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
        
        # Store pour garder la sélection
        dcc.Store(id='selected-heuristic', data=None)
        
    ], style={'padding': '20px', 'backgroundColor': '#F8F9FA', 'minHeight': '100vh'})
    
    # Callback pour mettre à jour le graphe
    @app.callback(
        [Output('cytoscape-graph', 'elements'),
         Output('cytoscape-graph', 'stylesheet'),
         Output('info-panel', 'children'),
         Output('selected-heuristic', 'data')],
        [Input({'type': 'heuristic-btn', 'index': dash.dependencies.ALL}, 'n_clicks')],
        [State('selected-heuristic', 'data')]
    )
    def update_graph(n_clicks, current_selection):
        ctx = dash.callback_context
        
        if not ctx.triggered or all(n == 0 for n in n_clicks):
            # État initial
            elements, stylesheet = get_cytoscape_elements(None)
            info = html.Div([
                html.H3("Sélectionnez une heuristique pour commencer", 
                    style={'color': '#7F8C8D', 'textAlign': 'center'})
            ])
            return elements, stylesheet, info, None
        
        # Identifier quel bouton a été cliqué
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id:
            import json
            button_data = json.loads(button_id)
            selected = button_data['index']
            
            elements, stylesheet = get_cytoscape_elements(selected)
            
            h = heuristics[selected]
            path_str = ' → '.join(map(str, h['path']))
            
            info = html.Div([
                html.H2(h['name'], style={'color': '#2C3E50', 'marginBottom': '10px'}),
                html.H4(h['description'], style={'color': '#27ae60', 'marginBottom': '15px'}),
                html.P([
                    html.Strong("Chemin: ", style={'color': '#34495E'}),
                    html.Span(path_str, style={'color': '#e040fb', 'fontSize': '16px', 'fontFamily': 'monospace'})
                ]),
                html.Hr(style={'margin': '15px 0'}),
                html.P(f"Nombre de sauts: {len(h['path']) - 1}", style={'color': '#7F8C8D'})
            ])
            
            return elements, stylesheet, info, selected
        
        return dash.no_update, dash.no_update, dash.no_update, current_selection
    
    print(f"\n{'='*60}")
    print(f"Dashboard lancé sur http://127.0.0.1:{port}")
    print(f"{'='*60}")
    print(f"Heuristiques disponibles: {len([h for h in heuristics.values() if h])}")
    print(f"Cliquez sur les boutons pour explorer les différents chemins")
    print(f"{'='*60}\n")
    
    app.run(debug=False, port=port)


# Fonction simplifiée pour le main.py
def show_all_heuristics(graph, start, end, port=8050):
    """
    Fonction ultra-simple à appeler depuis main.py
    Usage: show_all_heuristics(g, 1, 11)
    """
    create_interactive_dashboard(graph, start, end, port)