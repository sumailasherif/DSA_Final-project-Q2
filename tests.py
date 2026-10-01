"""These are our correctness checks, we run them before any timing (same idea as in our sorting coursework)."""
from itertools import combinations
from math import comb

from road_network import (load_road_network, load_residential_areas, build_graph, count_roads,
                          generate_random_network, build_trap_network)
from shortest_paths import dijkstra, fastest_route, road_times_along, fewest_roads_route, all_pairs_check
from stop_placement import build_coverage, areas_covered_by, greedy_place_stops, exhaustive_best_stops