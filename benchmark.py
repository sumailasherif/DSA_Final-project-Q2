import csv
import gc
import os
import statistics
from math import comb
from time import perf_counter

from road_network import (load_road_network, load_residential_areas,
                          generate_random_network, build_trap_network)
from shortest_paths import fastest_route, all_pairs_check
from stop_placement import Q, MAX_MINUTES, build_coverage, greedy_place_stops, all_greedy_outcomes, exhaustive_best_stops

# All CSVs and charts go into a results folder next to this file.
OUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
TRIALS = 5      # timed runs per measurement, we report the median
WARM_UPS = 3    # untimed runs before we start the clock

"""This function returns the median time in seconds for ONE call of func."""
def median_time(func, runs: int = TRIALS, warmup: int = WARM_UPS, batch: int = 1) -> float:
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
    os.makedirs(OUT_FOLDER, exist_ok=True)
    path = os.path.join(OUT_FOLDER, filename)
    fieldnames = []
    for row in rows:                      # we collect every column name, in the order we first see them
        fieldnames += [key for key in row if key not in fieldnames]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()})
    print(f"  -> results/{filename}")
    return path


"""This function times and counts every step on the real Mauritius network."""
def measure_real_network() -> list[dict]:
    print("\n[1] Real network timings")
    g, a = load_road_network(), load_residential_areas()
    cov, _ = build_coverage(g, a)
    rows = []

    # One Dijkstra for the Curepipe to Pamplemousses route.
    _, _, s = fastest_route(g, "Curepipe", "Pamplemousses")
    t = median_time(lambda: fastest_route(g, "Curepipe", "Pamplemousses"), batch=2000)
    rows.append({"step": "Dijkstra, fastest route", "median_ms": t * 1000,
                 "main_operation": "relaxations", "count": s["relaxations"],
                 "other_counts": f"pops={s['pops']} stale={s['stale_pops']} edge_checks={s['edge_checks']}"})

    # The coverage table with full Dijkstra searches, then with the 9-minute cutoff, to compare the two.
    _, s = build_coverage(g, a, use_cutoff=False)
    t = median_time(lambda: build_coverage(g, a, use_cutoff=False), batch=200)
    rows.append({"step": "Coverage, no cutoff", "median_ms": t * 1000,
                 "main_operation": "relaxations", "count": s["relaxations"],
                 "other_counts": f"pops={s['pops']} stale={s['stale_pops']} edge_checks={s['edge_checks']}"})

    _, s = build_coverage(g, a, use_cutoff=True)
    t = median_time(lambda: build_coverage(g, a, use_cutoff=True), batch=200)
    rows.append({"step": "Coverage, 9 min cutoff", "median_ms": t * 1000,
                 "main_operation": "relaxations", "count": s["relaxations"],
                 "other_counts": f"pops={s['pops']} stale={s['stale_pops']} edge_checks={s['edge_checks']}"})

    # Floyd-Warshall, the alternative we rejected, so we can compare its cost.
    _, s = all_pairs_check(g)
    t = median_time(lambda: all_pairs_check(g), batch=20)
    rows.append({"step": "Floyd-Warshall (not used)", "median_ms": t * 1000,
                 "main_operation": "inner_steps", "count": s["inner_steps"], "other_counts": ""})

    # Greedy and exhaustive, timing only the stop-picking step since both share the same table.
    stops, covered, _, s = greedy_place_stops(cov, Q)
    t = median_time(lambda: greedy_place_stops(cov, Q), batch=1000)
    rows.append({"step": f"Greedy, {Q} stops", "median_ms": t * 1000,
                 "main_operation": "gain_evaluations", "count": s["gain_evaluations"],
                 "other_counts": f"covered={len(covered)} stops={'/'.join(stops)}"})

    best, n, s = exhaustive_best_stops(cov, a, Q)
    t = median_time(lambda: exhaustive_best_stops(cov, a, Q))
    rows.append({"step": f"Exhaustive, {Q} stops", "median_ms": t * 1000,
                 "main_operation": "subsets_evaluated", "count": s["subsets_evaluated"],
                 "other_counts": f"covered={n} optimal_sets={s['optimal_sets']} or_ops={s['or_operations']} stops={'/'.join(best)}"})

    # We print a short summary and save everything to CSV.
    for r in rows:
        print(f"  {r['step']:26} {r['median_ms']:10.4f} ms   {r['main_operation']}={r['count']}")
    save_csv(rows, "real_network_results.csv")
    return rows


"""This function runs greedy and exhaustive for 1 to 8 stops, to see where they agree and where they don't."""
def coverage_vs_stops(max_k: int = 8) -> list[dict]:
    print("\n[2] Stops vs coverage")
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
        print(f"  k={k}: greedy {len(gc_):2}  best {ec:2}  gap {ec - len(gc_)}  "
              f"(ties: {min(outcomes)}-{max(outcomes)})")
    save_csv(rows, "coverage_vs_stops.csv")
    return rows


"""This function checks how much our answer depends on the A-Z tie-break and on the 9-minute limit.

We try limits of 8, 9 and 10 minutes, greedy with A-Z and Z-A tie-breaks,
and every possible tie-break path, and compare them all to the true best.
"""
def tie_break_and_threshold() -> list[dict]:
    print("\n[3] Tie-break and minute limit")
    g, a = load_road_network(), load_residential_areas()
    rows = []
    # Same six stops, but a different minute limit each time.
    for limit in (8, 9, 10):
        cov, _ = build_coverage(g, a, limit=limit)
        _, alpha, _, _ = greedy_place_stops(cov, Q)
        _, rev, _, _ = greedy_place_stops(cov, Q, order=sorted(cov, reverse=True))
        _, best, _ = exhaustive_best_stops(cov, a, Q)
        outcomes = all_greedy_outcomes(cov, Q)
        rows.append({"limit_minutes": limit, "greedy_alphabetical": len(alpha),
                     "greedy_reverse_alphabetical": len(rev), "optimal": best,
                     "greedy_outcomes_over_all_tiebreaks": " ".join(f"{c}:{n}" for c, n in outcomes.items())})
        print(f"  {limit:2} min: A-Z {len(alpha)}, Z-A {len(rev)}, best {best}, all ties {outcomes}")
    save_csv(rows, "tie_break_and_threshold.csv")
    return rows


"""This function runs our trap network at different sizes, with k = 2 (greedy loses) and k = 3 (they agree)."""
def counterexample_table() -> list[dict]:
    print("\n[4] Trap network")
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
            print(f"  m={m:2} k={k}: greedy {len(gc_):2} ({'/'.join(gs)}), best {ec:2} ({'/'.join(es)}), gap {ec - len(gc_)}")
    save_csv(rows, "counterexample.csv")
    return rows

"""This function builds one random network with v junctions and times greedy and exhaustive on it."""
def _scaling_row(v: int, k: int, seed: int, runs: int) -> dict:
    g, a = generate_random_network(v, seed=seed)

    # We time the coverage table once on its own, since it is shared work for both methods.
    start = perf_counter()
    cov, _ = build_coverage(g, a)
    coverage_ms = (perf_counter() - start) * 1000

    # Then we time only the stop-picking step for exhaustive and for greedy.
    _, n, s = exhaustive_best_stops(cov, a, k)
    exh_time = median_time(lambda: exhaustive_best_stops(cov, a, k), runs=runs, warmup=1)
    _, gcov, _, gs = greedy_place_stops(cov, k)
    greedy_time = median_time(lambda: greedy_place_stops(cov, k), batch=200)
    return {"V": v, "k": k, "C(V,k)": comb(v, k), "subsets_evaluated": s["subsets_evaluated"],
            "exhaustive_ms": exh_time * 1000, "us_per_subset": exh_time * 1e6 / s["subsets_evaluated"],
            "greedy_gain_evaluations": gs["gain_evaluations"], "greedy_ms": greedy_time * 1000,
            "coverage_table_ms_single_run": coverage_ms, "optimal": n, "greedy": len(gcov)}

"""This function shows how exhaustive grows when we keep 6 stops and make the network bigger.

C(V, 6) is a polynomial of degree 6, so doubling V should get close to x64 for big V.
We also work out the ratio between each size and the one before it.
"""
def scaling_fixed_k(sizes=(12, 18, 24, 30, 36), k: int = Q) -> list[dict]:
    print(f"\n[5] Exhaustive, k fixed at {k}")
    rows = []
    for v in sizes:
        print(f"  V={v} ...", end="", flush=True)
        r = _scaling_row(v, k, seed=v, runs=TRIALS)
        rows.append(r)
        print(f" {r['C(V,k)']:>9,} sets  exhaustive {r['exhaustive_ms']:9.1f} ms  greedy {r['greedy_ms']:.3f} ms")
    # We compare each size with the one before it, for both the subset count and the time.
    for prev, cur in zip(rows, rows[1:]):
        cur["count_ratio_vs_previous"] = cur["C(V,k)"] / prev["C(V,k)"]
        cur["time_ratio_vs_previous"] = cur["exhaustive_ms"] / prev["exhaustive_ms"]
    rows[0]["count_ratio_vs_previous"] = rows[0]["time_ratio_vs_previous"] = ""
    # The doubling check from 18 to 36 junctions, the key number for the report.
    base = next((r for r in rows if r["V"] == 18), None)
    double = next((r for r in rows if r["V"] == 36), None)
    if base and double:
        print(f"  18 -> 36 junctions: sets x{double['C(V,k)'] / base['C(V,k)']:.1f}, "
              f"time x{double['exhaustive_ms'] / base['exhaustive_ms']:.1f}")
    save_csv(rows, "scaling_fixed_k.csv")
    return rows

"""This function shows what happens when the number of stops grows with the network (k = V/3).

This is the case that makes the problem NP-hard. We actually run it up to V = 24, then for
bigger networks we only count the subsets and estimate the time from our measured speed,
because running them for real would take minutes, days or even years.
"""
def scaling_growing_k(sizes=(9, 12, 15, 18, 21, 24), projected=(30, 36, 45, 60)) -> list[dict]:
    print("\n[6] Exhaustive, k = V/3")
    rows = []
    for v in sizes:
        print(f"  V={v} ...", end="", flush=True)
        r = _scaling_row(v, v // 3, seed=100 + v, runs=TRIALS)
        r["measured"] = "yes"
        rows.append(r)
        print(f" k={v // 3}  {r['C(V,k)']:>11,} sets  {r['exhaustive_ms']:9.1f} ms")
    # We use the speed from our biggest real run to estimate the bigger ones.
    speed_us = rows[-1]["us_per_subset"]
    for v in projected:
        k = v // 3
        rows.append({"V": v, "k": k, "C(V,k)": comb(v, k), "subsets_evaluated": "",
                     "exhaustive_ms": comb(v, k) * speed_us / 1000, "us_per_subset": speed_us,
                     "greedy_gain_evaluations": "", "greedy_ms": "", "coverage_table_ms_single_run": "",
                     "optimal": "", "greedy": "", "measured": "projected"})
        secs = comb(v, k) * speed_us / 1e6
        print(f"  V={v} k={k}: {comb(v, k):,} sets -> about {_human(secs)} (estimate)")
    save_csv(rows, "scaling_growing_k.csv")
    return rows

"""This function turns seconds into minutes, hours, days or years so the big numbers are easy to read."""
def _human(seconds: float) -> str:
    for unit, size in (("years", 31_536_000), ("days", 86_400), ("hours", 3600), ("minutes", 60)):
        if seconds >= size:
            return f"{seconds / size:,.1f} {unit}"
    return f"{seconds:,.2f} seconds"


"""This function runs all six measurement sections and returns their rows."""
def run_all_measurements() -> dict:
    return {
        "real": measure_real_network(),
        "coverage_vs_k": coverage_vs_stops(),
        "tie_threshold": tie_break_and_threshold(),
        "counterexample": counterexample_table(),
        "fixed_k": scaling_fixed_k(),
        "growing_k": scaling_growing_k(),
    }


# matplotlib is only loaded inside plot_all(), so the measurements still run without it.
plt = None

"""This function reads a CSV from the results folder back into a list of rows."""
def load(filename: str) -> list[dict]:
    with open(os.path.join(OUT_FOLDER, filename)) as f:
        return list(csv.DictReader(f))

"""This chart shows greedy against the true best for 1 to 8 stops, so we can see where the gap opens."""
def plot_coverage_vs_stops(output: str = "coverage_vs_stops.png") -> None:
    rows = load("coverage_vs_stops.csv")
    k = [int(r["k"]) for r in rows]
    plt.figure(figsize=(7, 4.5))
    plt.plot(k, [int(r["optimal"]) for r in rows], marker="o", color="#16A085", label="Best possible")
    plt.plot(k, [int(r["greedy"]) for r in rows], marker="s", linestyle="--", color="#C0392B", label="Greedy")
    plt.axhline(18, color="grey", linewidth=0.8, linestyle=":")
    plt.text(1, 18.2, "all 18 areas", color="grey", fontsize=8)
    plt.xlabel("Number of bus stops")
    plt.ylabel(f"Areas covered (within {MAX_MINUTES} min)")
    plt.title("Greedy vs best possible coverage")
    plt.xticks(k)
    plt.yticks(range(0, 19, 3))     # whole areas only, no 2.5 or 7.5
    plt.ylim(0, 19.5)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    _save(output)

"""This chart shows how exhaustive search grows: sets to check on the left, time taken on the right."""
def plot_exhaustive_scaling(output: str = "exhaustive_scaling.png") -> None:
    fixed = load("scaling_fixed_k.csv")
    growing = load("scaling_growing_k.csv")
    measured = [r for r in growing if r["measured"] == "yes"]
    projected = [r for r in growing if r["measured"] == "projected"]

    # Left panel: how many sets of stops exhaustive has to check.
    fig, (left, right) = plt.subplots(1, 2, figsize=(11, 4.5))
    fig.suptitle("How exhaustive search grows with the network")
    left.plot([int(r["V"]) for r in fixed], [int(r["C(V,k)"]) for r in fixed],
              marker="o", color="#2471A3", label=f"{Q} stops")
    left.plot([int(r["V"]) for r in measured], [int(r["C(V,k)"]) for r in measured],
              marker="o", color="#C0392B", label="1 stop per 3 junctions")
    left.plot([int(measured[-1]["V"])] + [int(r["V"]) for r in projected],
              [int(measured[-1]["C(V,k)"])] + [int(r["C(V,k)"]) for r in projected],
              linestyle="--", color="#C0392B", alpha=0.6, label="1 stop per 3 junctions (estimated)")
    left.set_yscale("log")
    left.set_xlabel("Number of junctions")
    left.set_ylabel("Sets of stops to check (log scale)")
    left.set_title("Work needed")
    left.legend(fontsize=8)
    left.grid(True, which="both", alpha=0.3)

    # Right panel: the times we actually measured, with greedy added for comparison.
    right.plot([int(r["V"]) for r in fixed], [float(r["exhaustive_ms"]) for r in fixed],
               marker="o", color="#2471A3", label=f"Exhaustive, {Q} stops")
    right.plot([int(r["V"]) for r in measured], [float(r["exhaustive_ms"]) for r in measured],
               marker="o", color="#C0392B", label="Exhaustive, 1 stop per 3 junctions")
    right.plot([int(r["V"]) for r in fixed], [float(r["greedy_ms"]) for r in fixed],
               marker="s", color="#7D3C98", label=f"Greedy, {Q} stops")
    right.set_yscale("log")
    right.set_xlabel("Number of junctions")
    right.set_ylabel("Time in ms (log scale)")
    right.set_title("Time taken")
    right.legend(fontsize=8)
    right.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    _save(output)

"""This chart shows the trap network, where greedy falls further behind as the network grows."""
def plot_counterexample(output: str = "counterexample_gap.png") -> None:
    rows = [r for r in load("counterexample.csv") if r["k"] == "2"]
    m = [int(r["m"]) for r in rows]
    plt.figure(figsize=(7, 4.5))
    plt.plot(m, [int(r["optimal"]) for r in rows], marker="o", color="#16A085", label="Best (West + East)")
    plt.plot(m, [int(r["greedy"]) for r in rows], marker="s", linestyle="--", color="#C0392B", label="Greedy (Centre first)")
    # We write the gap under each greedy point so it is easy to read.
    for r in rows:
        plt.annotate(f"gap {r['gap']}", (int(r["m"]), int(r["greedy"])), textcoords="offset points",
                     xytext=(0, -14), ha="center", fontsize=8)
    plt.xlabel("Areas around each hub")
    plt.ylabel("Areas covered with 2 stops")
    plt.title("Trap network: greedy falls further behind")
    plt.xticks(m)
    plt.ylim(0, max(int(r["optimal"]) for r in rows) + 3)     # room under the lowest point for its gap label
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    _save(output)

def _save(name: str) -> None:
    path = os.path.join(OUT_FOLDER, name)
    plt.savefig(path, dpi=150)
    plt.close("all")
    print(f"  -> results/{name}")

"""This function loads matplotlib, then draws and saves all three charts."""
def plot_all() -> None:
    global plt
    try:
        import matplotlib
        matplotlib.use("Agg")           # we save the charts as files, so no pop-up window is needed
        import matplotlib.pyplot as plt
    except ImportError:
        print("  No matplotlib, skipping charts (pip install matplotlib)")
        return
    plot_coverage_vs_stops()
    plot_exhaustive_scaling()
    plot_counterexample()

if __name__ == "__main__":
    run_all_measurements()
    plot_all()
