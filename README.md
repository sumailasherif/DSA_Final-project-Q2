# DSA Final Project, Question 2: A new bus route and where to put the stops

This Data Structures and Algorithms final project models the Mauritius road network as a weighted graph.
I used it  to answer two questions:

1. **What is the fastest bus route from Curepipe to Pamplemousses?** We answer this with Dijkstra's algorithm.
2. **Where should we put six bus stops so that as many residential areas as possible are covered?**
   An area is covered if the shortest travel time between a stop and the area's junction is
   **at most nine minutes (exactly 9 counts)**. We answer this with the greedy rule the question asks for,
   and we compare it against the baseline: an exhaustive search over all C(18, 6) = 18,564 ways to pick six stops.

## Project Overview

The point of this project is to show, with real numbers instead of just the theory, when a greedy rule is good enough
and why it can never be guaranteed to find the best answer.

Running `python main.py --all` does four things:

1. It runs **11 correctness checks** first. If any check fails, the program stops before timing anything,
   because timing wrong code is pointless.
2. It prints **the answers**: the fastest route, the greedy stops round by round, the exhaustive best stops and the gap,
   and our own "trap" network where greedy loses by more.
3. It **measures** everything. It uses warm-up runs and the median of 5 runs, and it counts operations next to the time.
   It also checks how exhaustive search grows on bigger random networks.
4. It saves **6 CSV files and 3 charts** into the `results/` folder for the report.

## Requirements

- **Python 3.10 or newer** (we used Python 3.13). We use `int.bit_count()` and the `X | None` type hints, which need 3.10+.
- **matplotlib**, only for the charts. If it is missing, everything else still runs and the charts are skipped with a message.

## How to Run

**1. Get the code and open the folder**
```bash
git clone https://github.com/sumailasherif/DSA_Final-project-Q2.git
cd DSA_Final-project-Q2
```

**2. Install matplotlib**
```bash
python -m pip install -r requirements.txt
```
(On Windows, if `pip` is "not recognized", use `python -m pip ...` exactly as written above.)

**3. Run the whole project (checks, answers, measurements, CSVs and charts)**
```bash
python main.py --all
```
This takes under a minute on a normal laptop. Most of the time goes on the scaling test with 36 junctions.

**4. Or use the menu**
```bash
python main.py
```

**5. Or run one part on its own**
```bash
python tests.py            # the 11 correctness checks only
python road_network.py     # prints the network we loaded
python shortest_paths.py   # fastest route, fewest-roads route, Floyd-Warshall check
python stop_placement.py   # coverage table, greedy rounds, exhaustive best
python benchmark.py        # all measurements, CSVs and charts
```

All files find the CSVs next to themselves, so you can run them from any folder in VS Code.

## Project Structure

```
DSA_Final-project-Q2/
│
├── main.py                       the menu, and --all to run everything
├── road_network.py               loads the real network, builds random and trap networks
├── shortest_paths.py             Dijkstra, BFS, Floyd-Warshall
├── stop_placement.py             9-minute coverage table, greedy, exhaustive search
├── tests.py                      11 correctness checks
├── benchmark.py                  timings, operation counts, CSVs and charts
│
├── Q2_road_network.csv           25 rows of roads with travel times (minutes)
├── Q2_residential_areas.csv      18 residential areas and their junctions
├── requirements.txt              matplotlib
│
├── results/                      created by benchmark.py
│   ├── real_network_results.csv
│   ├── coverage_vs_stops.csv
│   ├── tie_break_and_threshold.csv
│   ├── counterexample.csv
│   ├── scaling_fixed_k.csv
│   ├── scaling_growing_k.csv
│   ├── coverage_vs_stops.png
│   ├── exhaustive_scaling.png
│   └── counterexample_gap.png
│
└── README.md
```

## File Descriptions

| File | What is inside |
|---|---|
| `main.py` | The interactive menu and `--all`. It ties every other file together, like `Main.py` in our sorting coursework. |
| `road_network.py` | `load_road_network` reads the roads into an **adjacency list** and keeps each road once. `load_residential_areas` maps each area to its junction. `generate_random_network` builds random networks with the same density as the real one, for scaling tests. `build_trap_network` builds our counterexample. |
| `shortest_paths.py` | `dijkstra` uses a **binary heap** (`heapq`) with lazy deletion and an optional cutoff, and counts its operations. `fastest_route` and `build_path` give the route. `fewest_roads_route` is BFS (optional extra). `all_pairs_check` is Floyd-Warshall, the alternative we did not choose, which we use to check Dijkstra. |
| `stop_placement.py` | `build_coverage` runs one Dijkstra from each junction, stopping at 9 minutes. `greedy_place_stops` is the greedy rule with the alphabetical tie-break. `all_greedy_outcomes` follows every possible tie. `exhaustive_best_stops` tries all C(V, k) sets using **bitmasks**. |
| `tests.py` | 11 checks. They run before any timing. |
| `benchmark.py` | Six measurement sections and three charts. Everything is saved to `results/`. |

## Program Flow

```
Start
|
v
Load the network and build the 9-minute coverage table once
|
v
Show menu
|
|--- 1 --> Show the road network
|--- 2 --> Fastest route Curepipe -> Pamplemousses (Dijkstra)
|--- 3 --> Coverage table (areas within 9 minutes of each junction)
|--- 4 --> Greedy: place 6 stops, round by round, showing ties
|--- 5 --> Exhaustive: best 6 stops and the gap to greedy
|--- 6 --> Counterexample: the trap network where greedy loses by more
|--- 7 --> Extras: fewest-roads route (BFS) and coverage for 1 to 8 stops
|--- 8 --> Run everything: checks, answers, measurements, CSVs, charts
|--- 9 --> Exit
```

## The Data and Our Assumptions

- **Every road is two-way**, as the question says. The time from a stop to an area is the same as from the area to the stop.
- **The road CSV has 25 rows but only 24 real roads.** "Moka, St Pierre, 8" and "St Pierre, Moka, 8" are the same road
  written twice. We keep it once and print a note when loading. Keeping it twice would not change any shortest path,
  but it would add an extra adjacency entry that Dijkstra checks for nothing.
- **Exactly 9 minutes counts as covered**, so the code uses `<=`. `test_exactly_nine_counts` checks this boundary.
- **Stops can only be placed at the 18 junctions**, and each area is covered through the junction it sits at.
- **Ties in greedy go to the alphabetically first junction name.** We check junctions in A to Z order and only replace
  the current best if the new one is strictly better. All junction names start with a capital letter, so Python's
  string order is the same as alphabetical order.
- **Travel times must be zero or more.** Dijkstra needs this, so the loader stops with an error on a negative time.

## Results That Do Not Depend on the Machine

These numbers are the same on every computer. Timings in milliseconds depend on the machine, so they are in
`results/real_network_results.csv` and in the report.

| What | Result |
|---|---|
| Fastest route | Curepipe → Forest Side → Phoenix → Quatre Bornes → Rose Hill → Beau Bassin → Port Louis → Terre Rouge → Pamplemousses, **59 minutes, 8 roads** |
| Fewest roads (BFS, optional) | 6 roads but **65 minutes**, because it uses the 25-minute Quatre Bornes to Port Louis road |
| Greedy six stops | Quatre Bornes, Arsenal, Curepipe, Ebene, Moka, Pailles → **17 of 18 areas** |
| Exhaustive best six | Arsenal, Curepipe, Moka, Pailles, Quatre Bornes, Trou aux Biches → **18 of 18 areas** (3 different sets reach 18) |
| Gap on the real network | **1 area**. It comes from one tie in round 4: Ebene and Moka both add 3, and A to Z picks Ebene. |
| Greedy over every possible tie-break | 360 tie-break paths end on 17, and 24 paths end on 18 |
| Number of stops 1 to 8 | Greedy matches the best for k = 1, 2, 3, 4, 7 and 8. It is 1 short for k = 5 and 6 |
| Trap network (m = 8, k = 2) | Greedy 13, best 16, **gap 3, with no tie involved**. The gap grows as m/2 − 1 (1, 3, 5, 7 for m = 4, 8, 12, 16) |

**Operation counts on the real network**

| Step | Main operation | Count |
|---|---|---|
| Dijkstra, one route (full search) | relaxations | 19 (20 pops, 2 stale, 48 edge checks) |
| Coverage table, 18 Dijkstras, full search | relaxations | 352 |
| Coverage table, 18 Dijkstras, stopping at 9 minutes | relaxations | 111 |
| Floyd-Warshall (rejected alternative) | inner steps | 5,832 (= 18³) |
| Greedy, 6 stops | gain evaluations | 93 |
| Exhaustive, 6 stops | subsets checked | 18,564 (111,384 OR operations) |

## How We Measured

We followed the "Measuring running time" rules from the brief:

- **Warm up first.** Each function runs a few times before the clock starts.
- **Repeat and take the median.** We use 5 timed runs and report the median.
- **Garbage collection is switched off during each timed run**, like Python's `timeit` does.
- **Very fast functions are batched.** One Dijkstra takes microseconds, so it runs many times inside each timed run, and we divide.
- **We count operations next to the clock.** We count relaxations, gain evaluations and subsets checked. The counts grow
  exactly as the Big-O analysis says, while the clock also measures the machine.
- **We only time the part that differs.** Greedy and exhaustive both use the same coverage table, so the table is built
  once and timed on its own. Only the stop-picking step is timed for each method.

## Correctness Checks (`tests.py`)

| Check | What it proves |
|---|---|
| `test_loading` | 18 junctions, 24 roads after the duplicate, 18 areas, every road two-way |
| `test_dijkstra_matches_all_pairs_check` | Dijkstra agrees with Floyd-Warshall on every pair, on the real network and 15 random ones |
| `test_fastest_route` | The route is 59 minutes, its road times add up, and the way back takes the same time |
| `test_cutoff_gives_same_coverage` | Stopping Dijkstra at 9 minutes gives the same table with fewer relaxations |
| `test_exactly_nine_counts` | 9 minutes counts, 10 does not, and 4 + 5 over two roads counts |
| `test_alphabetical_tie_break` | In a tie, greedy picks the alphabetically first junction |
| `test_supplied_answers` | Greedy gets 17, exhaustive gets 18, and exhaustive checks exactly 18,564 sets |
| `test_greedy_never_beats_exhaustive` | Greedy is never better than exhaustive, and with one stop they are equal |
| `test_bitmask_search_matches_plain_sets` | The bitmask shortcut gives the same answer as a slow search with normal sets |
| `test_counterexample` | On the trap network greedy picks Centre with no tie, gets 13, and the best (East + West) gets 16 |
| `test_bfs_fewest_roads` | BFS finds a 6-road route that is slower than Dijkstra's 8-road route |

## How the Code Matches the Report

| Claim in the report | Where to see it in the code |
|---|---|
| Dijkstra uses a binary heap, because "get the closest unsettled junction" is its most frequent operation | `shortest_paths.dijkstra` uses `heapq` and counts `pops` and `stale_pops` |
| Coverage only needs times up to 9 minutes, so each search can stop early | `dijkstra(..., cutoff=9)` in `stop_placement.build_coverage`: 111 relaxations instead of 352 |
| Floyd-Warshall always does V³ steps however sparse the roads are | `shortest_paths.all_pairs_check`, `inner_steps` = 5,832 |
| Exhaustive search joins coverage sets many times, so we use bitmasks | `stop_placement.to_bitmasks` and `exhaustive_best_stops` (OR plus `bit_count`) |
| Greedy has no guarantee, and the loss is not only about the tie-break | `road_network.build_trap_network` and `benchmark.counterexample_table` |
| With 6 stops fixed, exhaustive grows like V⁶. When stops grow with the network, it grows exponentially | `benchmark.scaling_fixed_k` and `benchmark.scaling_growing_k`, plus the chart `exhaustive_scaling.png` |

## Limitations

- Travel times are fixed numbers. There is no traffic, time of day, or waiting time at stops.
- Coverage is all or nothing at exactly 9 minutes. An area 9.5 minutes away counts the same as one an hour away.
  `benchmark.tie_break_and_threshold` shows the answer changes if the limit is 8 or 10 minutes.
- Every area counts the same. We do not weight areas by how many people live there.
- Exhaustive search only works because 6 stops out of 18 is small. For much bigger networks with more stops it is not usable,
  which is exactly what the scaling tests show.
- The random networks used for scaling are not real road maps. They only match the real network's density.

The report discusses these limitations in more detail.

