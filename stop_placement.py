from shortest_paths import dijkstra

COVER_LIMIT = 9     # an area is covered if it is at most 9 minutes from a stop
 
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

"""This function turns each junction's coverage into a number where bit i is 1 if area i is covered."""

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

"""This function places k stops with greedy and returns (stops, covered areas, a log of each round, stats)."""
def greedy_place_stops(coverage: dict, k: int, order: list[str] | None = None) -> tuple[list[str], set, list[dict], dict]:
    candidates = list(order) if order is not None else sorted(coverage)
    stops, covered, log = [], set(), []
    stats = {"gain_evaluations": 0}     # how many times we checked a junction's gain

    for round_number in range(1, k + 1):
        best, best_gain, tied = None, -1, []

        # We check every junction we have not picked yet and count how many NEW areas it adds.
        for junction in candidates:
            if junction in stops:
                continue
            stats["gain_evaluations"] += 1
            gain = len(coverage[junction] - covered)     # only the areas not covered yet
            if gain > best_gain:
                best, best_gain, tied = junction, gain, [junction]
            elif gain == best_gain:
                tied.append(junction)                    # we note the ties so we can show them later

        if best is None:        # this only happens if there are fewer junctions than k
            break

        # We add the winner as a stop and mark its areas as covered.
        stops.append(best)
        new_areas = coverage[best] - covered
        covered |= new_areas


        # We save what happened this round so main.py can print it round by round.
        log.append({"round": round_number, "stop": best, "gain": best_gain,
                    "total": len(covered), "tied_with": [t for t in tied if t != best],
                    "new_areas": sorted(new_areas)})
    return stops, covered, log, stats


 #Running this file on its own prints what every junction covers, biggest first.
if __name__ == "__main__":
    from road_network import load_road_network, load_residential_areas
    g, a = load_road_network(), load_residential_areas()
    cov, s = build_coverage(g, a)
    for j in sorted(cov, key=lambda x: (-len(cov[x]), x)):
        print(f"{j:16} covers {len(cov[j]):2}: {sorted(cov[j])}")
    print("Operation counts (with 9-minute cutoff):", s)

