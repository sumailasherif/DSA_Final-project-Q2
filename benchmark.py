import csv
import gc
import os
import statistics
from math import comb
from time import perf_counter

from road_network import (load_road_network, load_residential_areas,
                          generate_random_network, build_trap_network)
from shortest_paths import fastest_route, all_pairs_check
from stop_placement import build_coverage, greedy_place_stops, all_greedy_outcomes, exhaustive_best_stops

# All CSVs and charts go into a results folder next to this file.
RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
RUNS = 5        # timed runs per measurement, we report the median
WARMUP = 3      # untimed runs before we start the clock
K = 6           # number of stops the question asks for

"""This function returns the median time in seconds for ONE call of func."""
def median_time(func, runs: int = RUNS, warmup: int = WARMUP, batch: int = 1) -> float:
    # Warm-up runs, we do not time these.
    for _ in range(warmup):
        func()

    # Timed runs, each one runs func `batch` times and we divide to get one call.
    times = []
    for _ in range(runs):
        gc.disable()
        start = perf_counter()
        for _ in range(batch):
            func()
        end = perf_counter()
        gc.enable()
        times.append((end - start) / batch)
    return statistics.median(times)

    """This function saves our results to a CSV in the results folder, rounding decimals to 4 places."""
def save_csv(rows: list[dict], filename: str) -> str:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, filename)
    fieldnames = []
    for row in rows:                      # we collect every column name, in the order we first see them
        fieldnames += [key for key in row if key not in fieldnames]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()})
    print(f"  saved {path}")
    return path


"""This function times and counts every step on the real Mauritius network."""
def measure_real_network() -> list[dict]:
    print("\n[1] Supplied network: every step, timed and counted")
    g, a = load_road_network(), load_residential_areas()
    cov, _ = build_coverage(g, a)
    rows = []

    # One Dijkstra for the Curepipe to Pamplemousses route.
    _, minutes, s = fastest_route(g, "Curepipe", "Pamplemousses")
    t = median_time(lambda: fastest_route(g, "Curepipe", "Pamplemousses"), batch=2000)
    rows.append({"step": "Dijkstra: fastest route (1 source, full search)", "median_ms": t * 1000,
                 "main_operation": "relaxations", "count": s["relaxations"],
                 "other_counts": f"pops={s['pops']} stale={s['stale_pops']} edge_checks={s['edge_checks']}"})

    # The coverage table with full Dijkstra searches, then with the 9-minute cutoff, to compare the two.
    _, s = build_coverage(g, a, use_cutoff=False)
    t = median_time(lambda: build_coverage(g, a, use_cutoff=False), batch=200)
    rows.append({"step": "Coverage table: 18 Dijkstras, full search", "median_ms": t * 1000,
                 "main_operation": "relaxations", "count": s["relaxations"],
                 "other_counts": f"pops={s['pops']} stale={s['stale_pops']} edge_checks={s['edge_checks']}"})

    _, s = build_coverage(g, a, use_cutoff=True)
    t = median_time(lambda: build_coverage(g, a, use_cutoff=True), batch=200)
    rows.append({"step": "Coverage table: 18 Dijkstras, stop at 9 min", "median_ms": t * 1000,
                 "main_operation": "relaxations", "count": s["relaxations"],
                 "other_counts": f"pops={s['pops']} stale={s['stale_pops']} edge_checks={s['edge_checks']}"})

    # Floyd-Warshall, the alternative we rejected, so we can compare its cost.
    _, s = all_pairs_check(g)
    t = median_time(lambda: all_pairs_check(g), batch=20)
    rows.append({"step": "Floyd-Warshall all pairs (rejected alternative)", "median_ms": t * 1000,
                 "main_operation": "inner_steps", "count": s["inner_steps"], "other_counts": ""})

    # Greedy and exhaustive, timing only the stop-picking step since both share the same table.
    stops, covered, _, s = greedy_place_stops(cov, K)
    t = median_time(lambda: greedy_place_stops(cov, K), batch=1000)
    rows.append({"step": f"Greedy {K} stops (selection only)", "median_ms": t * 1000,
                 "main_operation": "gain_evaluations", "count": s["gain_evaluations"],
                 "other_counts": f"covered={len(covered)} stops={'/'.join(stops)}"})

    best, n, s = exhaustive_best_stops(cov, a, K)
    t = median_time(lambda: exhaustive_best_stops(cov, a, K))
    rows.append({"step": f"Exhaustive {K} stops (selection only)", "median_ms": t * 1000,
                 "main_operation": "subsets_evaluated", "count": s["subsets_evaluated"],
                 "other_counts": f"covered={n} optimal_sets={s['optimal_sets']} or_ops={s['or_operations']} stops={'/'.join(best)}"})

    # We print a short summary and save everything to CSV.
    for r in rows:
        print(f"  {r['step']:50} {r['median_ms']:10.4f} ms   {r['main_operation']}={r['count']}")
    save_csv(rows, "real_network_results.csv")
    return rows

# ---------------------------------------------------------------- 1. The real network

"""This function times and counts every step on the real Mauritius network."""
def measure_real_network() -> list[dict]:
    print("\n[1] Supplied network: every step, timed and counted")
    g, a = load_road_network(), load_residential_areas()
    cov, _ = build_coverage(g, a)
    rows = []

    # One Dijkstra for the Curepipe to Pamplemousses route.
    _, minutes, s = fastest_route(g, "Curepipe", "Pamplemousses")
    t = median_time(lambda: fastest_route(g, "Curepipe", "Pamplemousses"), batch=2000)
    rows.append({"step": "Dijkstra: fastest route (1 source, full search)", "median_ms": t * 1000,
                 "main_operation": "relaxations", "count": s["relaxations"],
                 "other_counts": f"pops={s['pops']} stale={s['stale_pops']} edge_checks={s['edge_checks']}"})

    # The coverage table with full Dijkstra searches, then with the 9-minute cutoff, to compare the two.
    _, s = build_coverage(g, a, use_cutoff=False)
    t = median_time(lambda: build_coverage(g, a, use_cutoff=False), batch=200)
    rows.append({"step": "Coverage table: 18 Dijkstras, full search", "median_ms": t * 1000,
                 "main_operation": "relaxations", "count": s["relaxations"],
                 "other_counts": f"pops={s['pops']} stale={s['stale_pops']} edge_checks={s['edge_checks']}"})

    _, s = build_coverage(g, a, use_cutoff=True)
    t = median_time(lambda: build_coverage(g, a, use_cutoff=True), batch=200)
    rows.append({"step": "Coverage table: 18 Dijkstras, stop at 9 min", "median_ms": t * 1000,
                 "main_operation": "relaxations", "count": s["relaxations"],
                 "other_counts": f"pops={s['pops']} stale={s['stale_pops']} edge_checks={s['edge_checks']}"})

    # Floyd-Warshall, the alternative we rejected, so we can compare its cost.
    _, s = all_pairs_check(g)
    t = median_time(lambda: all_pairs_check(g), batch=20)

    rows.append({"step": "Floyd-Warshall all pairs (rejected alternative)", "median_ms": t * 1000,
                 "main_operation": "inner_steps", "count": s["inner_steps"], "other_counts": ""})

    # Greedy and exhaustive, timing only the stop-picking step since both share the same table.
    stops, covered, _, s = greedy_place_stops(cov, K)
    t = median_time(lambda: greedy_place_stops(cov, K), batch=1000)
    rows.append({"step": f"Greedy {K} stops (selection only)", "median_ms": t * 1000,
                 "main_operation": "gain_evaluations", "count": s["gain_evaluations"],
                 "other_counts": f"covered={len(covered)} stops={'/'.join(stops)}"})

    best, n, s = exhaustive_best_stops(cov, a, K)
    t = median_time(lambda: exhaustive_best_stops(cov, a, K))
    rows.append({"step": f"Exhaustive {K} stops (selection only)", "median_ms": t * 1000,
                 "main_operation": "subsets_evaluated", "count": s["subsets_evaluated"],
                 "other_counts": f"covered={n} optimal_sets={s['optimal_sets']} or_ops={s['or_operations']} stops={'/'.join(best)}"})

    # We print a short summary and save everything to CSV.
    for r in rows:
        print(f"  {r['step']:50} {r['median_ms']:10.4f} ms   {r['main_operation']}={r['count']}")
    save_csv(rows, "real_network_results.csv")
    return rows