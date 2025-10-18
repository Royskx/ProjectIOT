from GraphStruct import  create_example_graph, count_routes
from Display import show_all_heuristics, show_colorful

g = create_example_graph()
#=========================================== display in terminal =========================================
show_colorful(g)
print("Nombre de routes de 1 à 11 :", count_routes(g, 1, 11))

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
