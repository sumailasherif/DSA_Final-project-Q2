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
        