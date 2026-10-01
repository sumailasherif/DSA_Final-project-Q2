import heapq


def dijkstra(graph: dict, source: str, cutoff: float | None = None) -> tuple[dict, dict, dict]:
    """This function returns our (dist, prev, stats) from the source junction.
    dist[j]  = the shortest time in minutes from source to j
    prev[j]  = the junction we came from, so we can rebuild the path to reach j
    stats    = how many pushes, pops, edge checks and relaxations we did.

    If we give a cutoff (like 9 minutes), the search stops once everything left
    is further than that, which is all we need for the coverage part"""
    if source not in graph:
        raise KeyError(f"Unknown junction: {source}")

    # Our source is 0 minutes from itself and it is the first thing in the heap.
    tentative = {source: 0}     # best time found so far for each junction (not final yet)
    prev = {source: None}
    settled = {}                # junctions whose shortest time is now final
    heap = [(0, source)]        # (time, junction), the heap always gives us the smallest time first
    stats = {"pushes": 1, "pops": 0, "stale_pops": 0, "edge_checks": 0, "relaxations": 0}

    while heap:
        # We take out the junction with the smallest time so far.
        time, node = heapq.heappop(heap)
        stats["pops"] += 1

        # If we already settled this junction, this is just an old entry, so we skip it.
        if node in settled:
            stats["stale_pops"] += 1
            continue

        # With a cutoff, once the smallest time is over the limit, everything else is too, so we stop our search.
        if cutoff is not None and time > cutoff:
            break
        settled[node] = time

        # Now we look at every road leaving this junction and see if it gives a faster time.
        for neighbour, minutes in graph[node]:
            stats["edge_checks"] += 1
            if neighbour in settled:
                continue
            new_time = time + minutes
            if neighbour not in tentative or new_time < tentative[neighbour]:
                # This is the relaxation step: we found a faster way, so we save it and push it on the heap.
                tentative[neighbour] = new_time
                prev[neighbour] = node
                heapq.heappush(heap, (new_time, neighbour))
                stats["relaxations"] += 1
                stats["pushes"] += 1

    # We only keep the path links for junctions we actually settled.
    prev = {j: p for j, p in prev.items() if j in settled}
    return settled, prev, stats


def build_path(prev: dict, target: str) -> list[str]:
    """This function walks backwards from the target using prev, then flips the list so it reads start to end."""
    if target not in prev:
        return []
    path = []
    node = target
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()
    return path


def fastest_route(graph: dict, start: str, end: str) -> tuple[list[str], int, dict]:
    """This function runs Dijkstra from start and gives us the route to end, the total minutes, and the stats."""
    dist, prev, stats = dijkstra(graph, start)
    if end not in dist:
        return [], -1, stats        # -1 means there is no way to get there
    return build_path(prev, end), dist[end], stats


def road_times_along(graph: dict, path: list[str]) -> list[int]:
    """This function gives the minutes for each road on a path, so we can print the route leg by leg."""
    legs = []
    for a, b in zip(path, path[1:]):
        legs.append(min(m for n, m in graph[a] if n == b))
    return legs

# ---------------------------------------------------------------- BFS: the route with the fewest roads (optional extra)

"""This function uses BFS to find the route with the FEWEST ROADS from start to end.
BFS does not look at the minutes at all, so fewer roads does not mean faster: one long road
(Quatre Bornes to Port Louis, 25 minutes) can replace a few short ones."""
def fewest_roads_route(graph: dict, start: str, end: str) -> list[str]:
    prev = {start: None}        # where we came from, also tells us which junctions we already visited
    queue = deque([start])      # BFS uses a queue, first in first out

    # We explore the network layer by layer: 1 road away, then 2 roads away, and so on.
    while queue:
        node = queue.popleft()
        if node == end:
            break
        for neighbour, _ in sorted(graph[node]):       # sorted so we get the same answer every run
            if neighbour not in prev:
                prev[neighbour] = node
                queue.append(neighbour)

    if end not in prev:
        return []
    return build_path(prev, end)    # same walk back as Dijkstra


if __name__ == "__main__":
    # Running this file on its own prints the Curepipe to Pamplemousses route.
    from road_network import load_road_network

    g = load_road_network()
    route, minutes, s = fastest_route(g, "Curepipe", "Pamplemousses")
    print(" -> ".join(route))
    print(f"Total: {minutes} minutes, {len(route) - 1} roads")
    print("Operation counts:", s)
