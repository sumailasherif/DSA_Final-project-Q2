from dijkstra import dijkstra
 
COVER_LIMIT = 9     # an area is covered if it is at most 9 minutes from a stopf
 
"""This function returns (coverage, total_stats), with one Dijkstra run from every junction."""
def build_coverage(graph: dict, areas: dict, limit: int = COVER_LIMIT,
                   use_cutoff: bool = True) -> tuple[dict, dict]:
    coverage = {}
    total = {"pushes": 0, "pops": 0, "stale_pops": 0, "edge_checks": 0, "relaxations": 0}

    for junction in sorted(graph):
        # We find the travel time from this junction to everything within the limit.
        dist, _, stats = dijkstra(graph, junction, cutoff=limit if use_cutoff else None)

          # Then we keep every area whose junction we reached in 9 minutes or less.
        coverage[junction] = frozenset(
            area for area, area_junction in areas.items()
            if area_junction in dist and dist[area_junction] <= limit
        )