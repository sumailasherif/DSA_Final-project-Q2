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

         # We add up the operation counts from all the Dijkstra runs.
        for key in total:
            total[key] += stats[key]
    return coverage, total

     
"""This function gives the full time[junction][area] table with no cutoff"""
def travel_time_table(graph: dict, areas: dict) -> dict:
    table = {}
    for junction in sorted(graph):
        dist, _, _ = dijkstra(graph, junction)
        table[junction] = {area: dist.get(j, float("inf")) for area, j in areas.items()}
    return table

"""This function joins the coverage of all the stops into one set of covered areas."""
def areas_covered_by(stops, coverage: dict) -> set:
    covered = set()
    for stop in stops:
        covered |= coverage[stop]
    return covered

"""This function turns each junction's coverage into a number where bit i is 1 if area i is covered.""""
def to_bitmasks(coverage: dict, areas: dict) -> tuple[list[str], list[int]]:
    area_index = {area: i for i, area in enumerate(sorted(areas))}   # gives every area its own bit position
    junctions = sorted(coverage)
    masks = []
    for j in junctions:
        m = 0
        for area in coverage[j]:
            m |= 1 << area_index[area]    
        masks.append(m)
    return junctions, masks

