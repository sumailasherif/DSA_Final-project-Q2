import sys
from math import comb

from road_network import load_road_network, load_residential_areas, count_roads, build_trap_network
from shortest_paths import fastest_route, road_times_along, fewest_roads_route
from stop_placement import (build_coverage, MAX_MINUTES, Q, greedy_place_stops,
                            all_greedy_outcomes, exhaustive_best_stops)
from tests import run_correctness_checks
from benchmark import run_all_measurements, plot_all

"""The two ends of our new bus route."""
ORIGIN, DESTINATION = "Curepipe", "Pamplemousses"

"""This function prints every junction and the roads that leave it, so we can see the whole network of roads."""
def show_network(graph: dict, areas: dict) -> None:
    print(f"\n{len(graph)} junctions, {count_roads(graph)} roads, {len(areas)} areas")
    for junction in sorted(graph):
        roads = ", ".join(f"{n} ({m} min)" for n, m in sorted(graph[junction]))
        print(f"  {junction:16} -> {roads}")

"""This function runs our Dijkstra and then prints the fastest route road by road, with the operation counts."""
def show_fastest_route(graph: dict) -> None:
    path, minutes, stats = fastest_route(graph, ORIGIN, DESTINATION)
    print(f"\n{ORIGIN} -> {DESTINATION}: {minutes} min, {len(path) - 1} roads")
    for (a, b), m in zip(zip(path, path[1:]), road_times_along(graph, path)):
        print(f"  {a:14} -> {b:16} {m:3} min")
    print(f"  {stats['relaxations']} relaxations, {stats['pops']} pops ({stats['stale_pops']} stale), "
          f"{stats['edge_checks']} edge checks")

"""This function prints which areas each junction covers within 9 minutes, starting with the biggest."""
def show_coverage(coverage: dict) -> None:
    print(f"\nAreas within {MAX_MINUTES} min of each junction:")
    for j in sorted(coverage, key=lambda x: (-len(coverage[x]), x)):
        print(f"  {j:16} {len(coverage[j]):2}  {', '.join(sorted(coverage[j]))}")

"""This function places the stops with greedy algorithm and prints each round, including any ties."""
def show_greedy(coverage: dict, k: int = Q) -> tuple:
    stops, covered, log, stats = greedy_place_stops(coverage, k)
    print(f"\nGreedy, {k} stops (ties go A-Z):")
    for row in log:
        tie = f"   tie: {', '.join(row['tied_with'])}" if row["tied_with"] else ""
        print(f"  Round {row['round']}: {row['stop']:15} +{row['gain']} -> {row['total']:2}{tie}")
    print(f"  {len(covered)} areas covered ({stats['gain_evaluations']} gain checks)")
    return stops, covered

"""This function finds the true best stops with exhaustive search and prints the gap to greedy."""
def show_exhaustive(coverage: dict, areas: dict, k: int = Q) -> None:
    _, covered = greedy_place_stops(coverage, k)[:2]
    best, n, stats = exhaustive_best_stops(coverage, areas, k)
    print(f"\nExhaustive, all {comb(len(coverage), k):,} sets of {k}:")
    print(f"  Best: {', '.join(best)} -> {n} areas ({stats['optimal_sets']} sets tie)")
    print(f"  Greedy {len(covered)}, best {n}, gap {n - len(covered)}")
    # We use this to also show what greedy would get if we followed every possible tie-break.
    outcomes = all_greedy_outcomes(coverage, k)
    print("  Other tie-breaks: " + ", ".join(f"{c} areas ({p} paths)" for c, p in outcomes.items()))

"""This function runs our trap network, where greedy loses by 3 areas without any tie."""
def show_counterexample(m: int = 8) -> None:
    g, a = build_trap_network(m)
    cov, _ = build_coverage(g, a)
    gs, gc, _, _ = greedy_place_stops(cov, 2)
    es, n, _ = exhaustive_best_stops(cov, a, 2)
    print(f"\nTrap network (m = {m}, {len(a)} areas, 2 stops):")
    print(f"  Centre {len(cov['Centre'])}, West {len(cov['West'])}, East {len(cov['East'])}")
    print(f"  Greedy : {', '.join(gs)} -> {len(gc)}")
    print(f"  Best   : {', '.join(es)} -> {n}  (gap {n - len(gc)}, no tie)")

"""These are the optional extras: the fewest-roads route with BFS, and coverage for 1 to 8 stops."""
def show_extras(graph: dict, coverage: dict, areas: dict) -> None:
    path = fewest_roads_route(graph, ORIGIN, DESTINATION)
    fast, minutes, _ = fastest_route(graph, ORIGIN, DESTINATION)

    print(f"\nBFS: {' -> '.join(path)}")
    print(f"  {len(path) - 1} roads, {sum(road_times_along(graph, path))} min "
          f"(Dijkstra: {len(fast) - 1} roads, {minutes} min)")
    print("\nStops vs coverage:")
    for k in range(1, 9):
        g = len(greedy_place_stops(coverage, k)[1])
        n = exhaustive_best_stops(coverage, areas, k)[1]
        print(f"  k={k}: greedy {g:2}  best {n:2}  gap {n - g}")

"""This function runs the whole project in order: checks, answers, measurements, then charts."""
def run_everything() -> None:
    graph, areas = load_road_network(verbose=True), load_residential_areas()
    coverage, _ = build_coverage(graph, areas)
    # We only measure if every check passes first.
    print("\n1) Checks")
    if not run_correctness_checks():
        print("Some checks failed, stopping here.")
        return
    print("\n2) Answers")
    show_fastest_route(graph)
    show_greedy(coverage)
    show_exhaustive(coverage, areas)
    show_counterexample()
    print("\n3) Timings (under a minute)")
    run_all_measurements()
    print("\n4) Charts")
    plot_all()

"""This function prints the menu options."""
def show_menu() -> None:
    print(f"\n--- {ORIGIN} -> {DESTINATION} bus route ---")
    print("1. Road network")
    print("2. Fastest route")
    print("3. Coverage table")
    print(f"4. Greedy ({Q} stops)")
    print(f"5. Exhaustive ({Q} stops)")
    print("6. Trap network")
    print("7. Extras (BFS, 1-8 stops)")
    print("8. Run everything")
    print("9. Exit")

"""This function loads the data once, then keeps showing the menu until we choose 9."""
def main() -> None:
    graph, areas = load_road_network(verbose=True), load_residential_areas()
    coverage, _ = build_coverage(graph, areas)
    # Each menu number points to the function it should run.
    actions = {
        "1": lambda: show_network(graph, areas),
        "2": lambda: show_fastest_route(graph),
        "3": lambda: show_coverage(coverage),
        "4": lambda: show_greedy(coverage),
        "5": lambda: show_exhaustive(coverage, areas),
        "6": show_counterexample,
        "7": lambda: show_extras(graph, coverage, areas),
        "8": run_everything,
    }
    while True:
        show_menu()
        choice = input("> ").strip()
        if choice == "9":
            print("Bye.")
            break
        if choice in actions:
            actions[choice]()
        else:
            print("Pick 1-9.")

# "python main.py --all" runs everything, "python main.py" opens the menu.
if __name__ == "__main__":
    if "--all" in sys.argv:
        run_everything()
    else:
        main()
