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


"""This function runs greedy and exhaustive for 1 to 8 stops, to see where they agree and where they don't."""
def coverage_vs_stops(max_k: int = 8) -> list[dict]:
    print("\n[2] Coverage against number of stops (greedy vs exhaustive)")
    g, a = load_road_network(), load_residential_areas()
    cov, _ = build_coverage(g, a)
    rows = []
    # For each number of stops we run both methods and also every possible tie-break.
    for k in range(1, max_k + 1):
        gs, gc_, _, _ = greedy_place_stops(cov, k)
        es, ec, s = exhaustive_best_stops(cov, a, k)
        outcomes = all_greedy_outcomes(cov, k)
        rows.append({"k": k, "greedy": len(gc_), "optimal": ec, "gap": ec - len(gc_),
                     "subsets_evaluated": s["subsets_evaluated"],
                     "best_greedy_any_tiebreak": max(outcomes), "worst_greedy_any_tiebreak": min(outcomes),
                     "greedy_stops": "/".join(gs), "optimal_stops": "/".join(es)})
        print(f"  k={k}: greedy {len(gc_):2}  optimal {ec:2}  gap {ec - len(gc_)}  "
              f"(any tie-break: {min(outcomes)}..{max(outcomes)})")
    save_csv(rows, "coverage_vs_stops.csv")
    return rows


"""This function checks how much our answer depends on the A-Z tie-break and on the 9-minute limit.

We try limits of 8, 9 and 10 minutes, greedy with A-Z and Z-A tie-breaks,
and every possible tie-break path, and compare them all to the true best.
"""
def tie_break_and_threshold() -> list[dict]:
    print("\n[3] How much of the result depends on the tie-break and on the 9-minute rule")
    g, a = load_road_network(), load_residential_areas()
    rows = []
    # Same six stops, but a different minute limit each time.
    for limit in (8, 9, 10):
        cov, _ = build_coverage(g, a, limit=limit)
        _, alpha, _, _ = greedy_place_stops(cov, K)
        _, rev, _, _ = greedy_place_stops(cov, K, order=sorted(cov, reverse=True))
        _, best, _ = exhaustive_best_stops(cov, a, K)
        outcomes = all_greedy_outcomes(cov, K)
        rows.append({"limit_minutes": limit, "greedy_alphabetical": len(alpha),
                     "greedy_reverse_alphabetical": len(rev), "optimal": best,
                     "greedy_outcomes_over_all_tiebreaks": " ".join(f"{c}:{n}" for c, n in outcomes.items())})
        print(f"  limit {limit:2} min: greedy A-Z {len(alpha)}, greedy Z-A {len(rev)}, optimal {best}, "
              f"all tie-break paths {outcomes}")
    save_csv(rows, "tie_break_and_threshold.csv")
    return rows


"""This function runs our trap network at different sizes, with k = 2 (greedy loses) and k = 3 (they agree)."""
def counterexample_table() -> list[dict]:
    print("\n[4] Constructed trap network (k = 2 and k = 3)")
    rows = []
    # Bigger m means a bigger trap, so the gap should keep growing when k = 2.
    for m in (4, 8, 12, 16):
        g, a = build_trap_network(m)
        cov, _ = build_coverage(g, a)
        for k in (2, 3):
            gs, gc_, _, _ = greedy_place_stops(cov, k)
            es, ec, _ = exhaustive_best_stops(cov, a, k)
            rows.append({"m": m, "k": k, "areas": len(a), "greedy": len(gc_), "optimal": ec,
                         "gap": ec - len(gc_), "greedy_stops": "/".join(gs), "optimal_stops": "/".join(es)})
            print(f"  m={m:2} k={k}: greedy {len(gc_):2} ({'/'.join(gs)}), optimal {ec:2} ({'/'.join(es)}), gap {ec - len(gc_)}")
    save_csv(rows, "counterexample.csv")
    return rows