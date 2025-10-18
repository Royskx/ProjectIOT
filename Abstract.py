import heapq
from GraphStruct import SimpleGraph
#heapq is a mini-python implementation of the heap structur which is etremely efficient to
#estabilish the order in the Dijekstra's algorithm.

#It uses internally the tabular structure, where children of node tab[i] are tab[2*i+1] and
#tab[2*i+2]

def best_path(graph, start, end, cost_func, maximize=False):
    # Dijkstra is a very efficient algorithm in order to calculate the shortest path
    # In a graph without negative cycles (otherwise it won't halt)

    if maximize:
        # For maximization, negate costs to use min-heap
        distances = {node: float('-inf') for node in graph.nodes()}
        distances[start] = 0

        # In the heap we are storing (negative_distance, node).
        # It is the induced graph structure for shortest path search.
        heap = [(0, start)]          
        multiplier = -1
    else:
        distances = {node: float('inf') for node in graph.nodes()}
        distances[start] = 0
        heap = [(0, start)]  # (distance, node)
        multiplier = 1
    
    # distances is a function that maps each node to R, it will be used to store the best 
    # distance found so far

    # precedents will represent at the end the following, 
    # precedents[v] is the preious node of v in the best path from start to end 
    precedent = {node: None for node in graph.nodes()}
    visited = set()
    
    while heap:
        current_dist, u = heapq.heappop(heap)
        current_dist *= multiplier  # Convert back to actual distance
        
        if u in visited:
            continue
        
        visited.add(u)
        

        # The intuition behind Dijkstra: imagine releasing tourists at a specific point on
        # the map. Each node will be reached first by tourists taking the shortest path to it.
        # In other words, when we pull a node out of the heap, means that all the tourists have 
        # Walked more than the shortest distance fomr the source to that node, therefore
        # the distance at that node is actually minimal. This explains why we can stop the moment
        # we pull out the destination node, at that moment we've already found the shortest path to it.
        if u == end:
            break
        
        # Skip if we found a better path already
        # The node u has already been sawn by another touriste who toke the shortest path to u
        if (maximize and current_dist < distances[u]) or \
           (not maximize and current_dist > distances[u]):
            continue
        
        # We take out the shortest path we have at this moment in the heap, then, we expand it 
        for v, (tmin, tmax) in graph.neighbors(u).items():
            cost = cost_func(u, v, tmin, tmax)
            new_distance = distances[u] + cost
            
            if maximize:
                if new_distance > distances[v]:
                    distances[v] = new_distance
                    precedent[v] = u
                    heapq.heappush(heap, (-new_distance, v))  # Negate, because the heap is ordered
                    # from the smallest to the greatest, this wouldn't interfere with negative cycles
                    # because when we pull out nodes of the heap, we use their positive distances as above.
            else:
                if new_distance < distances[v]:
                    distances[v] = new_distance
                    precedent[v] = u
                    heapq.heappush(heap, (new_distance, v))
    
    #path construction
    path = []
    current = end
    while current is not None:
        path.insert(0, current)
        current = precedent[current]
    
    if not path or path[0] != start:
        return None, float('inf') if not maximize else float('-inf')
    
    return path, distances[end]

#measures
def cost_min(u, v, tmin, tmax):
    return tmin

def cost_max(u, v, tmin, tmax):
    return tmax

def cost_marge(u, v, tmin, tmax):
    return tmax - tmin


#=================================== tests =====================================
def test_dense_graph():
    """Test 10: Graphe dense avec plusieurs alternatives"""
    g = SimpleGraph(directed=True)
    nodes = ['A', 'B', 'C', 'D', 'E']
    # Créer un graphe complet avec des coûts variables
    g.add_edge('A', 'B', 1, 3)
    g.add_edge('A', 'C', 4, 8)
    g.add_edge('A', 'D', 7, 12)
    g.add_edge('B', 'C', 2, 4)
    g.add_edge('B', 'E', 10, 15)
    g.add_edge('C', 'D', 1, 2)
    g.add_edge('C', 'E', 5, 9)
    g.add_edge('D', 'E', 1, 3)
    
    path, dist = best_path(g, 'A', 'E', cost_min)
    assert path == ['A', 'B', 'C', 'D', 'E'], f"Got {path}"
    assert dist == 5, f"Expected 5 (1+2+1+1), got {dist}"
    print("✓ Test 10 passed: Dense graph")

test_dense_graph()
