import sys
from math import comb

from langgraph import graph
 
from road_network import load_road_network, load_residential_areas, count_roads
from dijkstra import fastest_route, road_times_along
from coverage import build_coverage, COVER_LIMIT
from greedy_stops import greedy_place_stops, all_greedy_outcomes
from exhaustive_stops import exhaustive_best_stops
from counterexample import build_trap_network
from bfs import fewest_roads_route
from test import run_correctness_checks
from measurement import run_all_measurements
from results_plot import plot_all

"""The two ends of our new bus route."""
    START, END = "Curepipe", "Pamplemousses"

    """This function prints every junction and the roads that leaves it, so we can see the whole network of roads."""
    def show_network(graph: dict, areas: dict) -> None:
    print(f"\n{len(graph)} junctions, {count_roads(graph)} two-way roads, {len(areas)} residential areas")
    for junction in sorted(graph):
        roads = ", ".join(f"{n} ({m} min)" for n, m in sorted(graph[junction]))
        print(f"  {junction:16} -> {roads}")


    """This function runs our Dijkstra and then prints the fastest route road by road, with the operation counts."""
    def show_fastest_route(graph: dict) -> None:
        path, minutes, stats = fastest_route(graph, START, END)
    print(f"\nFastest route {START} -> {END}: {minutes} minutes over {len(path) - 1} roads")
    for (a, b), m in zip(zip(path, path[1:]), road_times_along(graph, path)):
        print(f"  {a:14} -> {b:16} {m:3} min")
    print(f"  Dijkstra did {stats['relaxations']} relaxations, {stats['pops']} heap pops "
          f"({stats['stale_pops']} stale), {stats['edge_checks']} edge checks")

    """This function prints which areas each junction covers within 9 minutes, starting with the biggest."""
    def show_coverage(coverage: dict) -> None:
        print(f"\nAreas each junction would cover (shortest time <= {COVER_LIMIT} minutes):")
    for j in sorted(coverage, key=lambda x: (-len(coverage[x]), x)):
        print(f"  {j:16} {len(coverage[j]):2}  {', '.join(sorted(coverage[j]))}")

    """This function places the stops with greedy algorithm and prints each round, including any ties."""
    def show_greedy(coverage: dict, k: int = 6) -> tuple:
        stops, covered, log, stats = greedy_place_stops(coverage, k)
    print(f"\nGreedy placement of {k} stops (ties -> alphabetical):")
    for row in log:
        tie = f"   tied with: {', '.join(row['tied_with'])}" if row["tied_with"] else ""
        print(f"  Round {row['round']}: {row['stop']:15} +{row['gain']} -> {row['total']:2} covered{tie}")
    print(f"  Greedy covers {len(covered)} areas ({stats['gain_evaluations']} gain evaluations)")
    return stops, covered

    """This function finds the true best stops with exhaustive search and prints the gap to greedy."""
    
    def show_exhaustive(coverage: dict, areas: dict, k: int = 6) -> None:
        _, covered = greedy_place_stops(coverage, k)[:2]
    best, n, stats = exhaustive_best_stops(coverage, areas, k)
    print(f"\nExhaustive search over all C({len(coverage)}, {k}) = {comb(len(coverage), k):,}
    
    print(f"  Best: {', '.join(best)} -> {n} areas  ({stats['optimal_sets']} different sets reach {n})")
    print(f"  Greedy {len(covered)} vs best {n}: gap = {n - len(covered)} area(s)")
    # We use this to also show what greedy would get if we followed every possible tie-break.
    outcomes = all_greedy_outcomes(coverage, k)
    print(f"  If every possible tie-break is followed, greedy ends on: "
          + ", ".join(f"{c} areas ({p} paths)" for c, p in outcomes.items())) sets of stops:")

    def show_counterexample(m: int = 8) -> None:
    """This function runs our trap network, where greedy loses by 3 areas without any tie."""
    g, a = build_trap_network(m)
    cov, _ = build_coverage(g, a)
    gs, gc, _, _ = greedy_place_stops(cov, 2)
    es, n, _ = exhaustive_best_stops(cov, a, 2)
    print(f"\nTrap network (m = {m}, {len(a)} areas, k = 2 stops):")
    print(f"  Coverage: Centre {len(cov['Centre'])}, West {len(cov['West'])}, East {len(cov['East'])}")
    print(f"  Greedy  : {', '.join(gs)} -> {len(gc)} areas")
    print(f"  Optimal : {', '.join(es)} -> {n} areas   (gap {n - len(gc)}, no tie involved)")