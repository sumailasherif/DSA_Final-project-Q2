rom dijkstra import dijkstra
 
COVER_LIMIT = 9     # an area is covered if it is at most 9 minutes from a stop
 
"""This function returns (coverage, total_stats), with one Dijkstra run from every junction."""
def build_coverage(graph: dict, areas: dict, limit: int = COVER_LIMIT,
                   use_cutoff: bool = True) -> tuple[dict, dict]:
    coverage = {}
    total = {"pushes": 0, "pops": 0, "stale_pops": 0, "edge_checks": 0, "relaxations": 0}