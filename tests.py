"""These are our correctness checks, we run them before any timing (same idea as in our sorting coursework)."""
from itertools import combinations
from math import comb

from road_network import (load_road_network, load_residential_areas, build_graph, count_roads,
                          generate_random_network, build_trap_network)
from shortest_paths import dijkstra, fastest_route, road_times_along, fewest_roads_route, all_pairs_check
from stop_placement import build_coverage, areas_covered_by, greedy_place_stops, exhaustive_best_stops

"""This checks the data loaded properly: 18 junctions, 24 roads (after the duplicate), 18 areas, two-way roads."""
def test_loading() -> None:
    g, a = load_road_network(), load_residential_areas()
    assert len(g) == 18, "expected 18 junctions"
    assert count_roads(g) == 24, "25 rows minus the duplicated Moka-St Pierre road = 24 roads"
    assert len(a) == 18 and set(a.values()) <= set(g), "every area must sit at a real junction"
    assert all(b in [n for n, _ in g[a_]] for a_ in g for b, _ in g[a_]), "roads must be two-way"