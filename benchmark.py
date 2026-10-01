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