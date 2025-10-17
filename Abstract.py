import heapq
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
        # In other words, the first time we visit a node is via the shortest path leading
        # to it. This explains why we can stop the moment we reach the destination node,
        # at that moment we've already found the shortest path to it.
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
                # the update of a distance to a node is performed at most once. It's a consequence
                # of what we have discussed earlier about tourists.
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
