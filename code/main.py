from GraphStruct import create_example_graph, count_routes, SimpleGraph
from Display import show_all_heuristics, show_colorful


# Example A: existing example graph
g = create_example_graph()
print("Example graph: show colorful output and count routes")
show_colorful(g)
print("Nombre de routes de 1 à 11 :", count_routes(g, 1, 11))


# Example B: construct from an edge list (flexible formats)
edge_list = [
	("A", "B", 2, 5),
	("B", "C", 3),        # single weight -> both tmin=tmax
	("C", "D"),         # no weights -> uses default
]
g2 = SimpleGraph.from_edge_list(edge_list, directed=True, default_weight=(1, 1))
print("Constructed graph from edge list with nodes:", g2.nodes())
show_colorful(g2)


# Example C: build from an adjacency dict
adj = {
	"x": {"y": (3, 7), "z": 4},  # mixed tuple and scalar
	"y": {"z": (2, 6)},
}
g3 = SimpleGraph.from_adj_dict(adj, directed=False)
print("Graph from adj dict edges:", g3.edges())
show_colorful(g3)


# Optionally relabel to consecutive integers (useful for some algorithms/visualizers)
g3_int, mapping = g3.relabel_to_ints(start=1)
print("Relabeled nodes mapping:", mapping)


#========================================= interactive HTML display ======================================
show_all_heuristics(g, 1, 11, port=8050)


#g = create_example_graph()
#g.show_colorful()
##g.draw_plotly()
#g_mean = g.make_converge(n_samples=1000)
#g_mean.show_colorful()
#
#g.draw_dash(port=8050)
#
#
#
#
##============================================ Additional criteria =================================================
##Empirical mean minimisation citeria
#path, val = best_path(g_mean, 1, 11, cost_min, maximize=False)
#print("Itinéraire optimiste :", path, "→ Temps min total :", val)
#g_mean.draw_dash(port=8050, path=path, heuristic_name="Gaussian Path", path_length=val)
#
#
##=========================================== Non abstract algorithms ===========================================
#print("\nNon-abstract algorithms results:")
#path, time = worst_case(g, 1, 11)
#g.draw_dash(port=8050, path=path, heuristic_name="Worst Case", path_length=time)
#
#print("Plus long chemin de 1 à 11 :", path, ". Temps max :", time)
#path, marge = most_stable_path(g, 1, 11)
#print("Itinéraire stable (1 → 11) :", path, "Marge de fluctuation minimale :", marge)
#g.draw_dash(port=8050, path=path, heuristic_name="Most Stable Path", path_length=marge)
#
##============================================= Abstract Algorithms ===============================================
#print("\n\nAbstract algorithms results:")
## Itinéraire optimiste (plus court chemin, minimisant le temps min)
#path, val = best_path(g, 1, 11, cost_min, maximize=False)
#print("Itinéraire optimiste :", path, "→ Temps min total :", val)
#g.draw_dash(port=8050, path=path, heuristic_name="Optimistic Path", path_length=val)
#
## Itinéraire prudent (plus long chemin, minimisant le temps max)
#path, val = best_path(g, 1, 11, cost_max, maximize=False)
#print("Itinéraire prudent :", path, "→ Temps max total :", val)
#g.draw_dash(port=8050, path=path, heuristic_name="Prudent Path", path_length=val)
#
## Itinéraire stable (plus court chemin, minimisant la marge)
#path, val = best_path(g, 1, 11, cost_marge, maximize=False)
#print("Itinéraire stable :", path, "→ Marge totale :", val)
#g.draw_dash(port=8050, path=path, heuristic_name="Stable Path", path_length=val)
#
## Itinéraire pire cas (plus long chemin, maximisant le temps max)
#path, val = best_path(g, 1, 11, cost_max, maximize=True)
#print("Pire Itinéraire :", path, "→ Temps max total :", val)
#g.draw_dash(port=8050, path=path, heuristic_name="Worst Path", path_length=val)
#
