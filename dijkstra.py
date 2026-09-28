import heapq

from distro import like
from traitlets import This
 
 #This function returns our (dist, prev, stats) from the source junction.
def dijkstra(graph: dict, source: str, cutoff: float | None = None) -> tuple[dict, dict, dict]:
     dist[j]  = the shortest time in minutes from source to j
    prev[j]  = the junction we came from to reach j, so we can rebuild the path
    stats    = how many pushes, pops, edge checks and relaxations we did
 
    """If we give a cutoff (like 9 minutes), the search stops once everything left
    is further than that, which is all we need for the coverage part"""

    def dijkstra(graph: dict, source: str, cutoff: float | None = None) -> tuple[dict, dict, dict]:
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