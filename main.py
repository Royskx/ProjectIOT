from GraphStruct import create_example_graph, count_routes
from Abstract import best_path, cost_min, cost_max, cost_marge
from NonAbstract import worst_case, most_stable_path

g = create_example_graph()
g.show()

print("Nombre de routes de 1 à 11 :", count_routes(g, 1, 11))

print("\nNon-abstract algorithms results:")
path, time = worst_case(g, 1, 11)
print("Plus long chemin de 1 à 11 :", path, ". Temps max :", time)
path, marge = most_stable_path(g, 1, 11)
print("Itinéraire stable (1 → 11) :", path, "Marge de fluctuation minimale :", marge)

print("\n\nAbstract algorithms results:")
# Itinéraire optimiste
path, val = best_path(g, 1, 11, cost_min, maximize=False)
print("Itinéraire optimiste :", path, "→ Temps min total :", val)

# Itinéraire prudent
path, val = best_path(g, 1, 11, cost_max, maximize=False)
print("Itinéraire prudent :", path, "→ Temps max total :", val)

# Itinéraire stable
path, val = best_path(g, 1, 11, cost_marge, maximize=False)
print("Itinéraire stable :", path, "→ Marge totale :", val)

# Itinéraire pire cas
path, val = best_path(g, 1, 11, cost_max, maximize=True)
print("Pire Itinéraire :", path, "→ Temps max total :", val)