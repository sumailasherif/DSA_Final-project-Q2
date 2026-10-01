import csv
import os
import random
 
HERE = os.path.dirname(os.path.abspath(__file__))
 
"""This helps us find the CSV file even if we run the code from a different folder in our  Code."""
def _path(filename: str) -> str:
    return filename if os.path.isabs(filename) else os.path.join(HERE, filename)

"""This function reads every road from the CSV and returns the graph."""
def load_road_network(filename: str = "Q2_road_network.csv", verbose: bool = False) -> dict:
    roads = {}          # key = the two junctions in sorted order, value = minutes
    duplicates = []     # any road we see a second time goes here as a duplicate
 
    # We read the file row by row and store each road only once.
    with open(_path(filename), newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            a, b = row["from"].strip(), row["to"].strip()
            minutes = int(row["minutes"])

            # Dijkstra only works with times that are zero or more, so we stop here if one is negative.
            if minutes < 0:
                raise ValueError(f"Negative travel time on {a}-{b}: Dijkstra needs non-negative weights")

            # Sorting the two names means Moka-St Pierre and St Pierre-Moka give the same key.
            key = tuple(sorted((a, b)))
            if key in roads:
                duplicates.append((a, b, minutes))
                roads[key] = min(roads[key], minutes)   # if they ever disagree we keep the faster one
            else:
                roads[key] = minutes

    graph = build_graph(roads)

    # When verbose is on we print a short summary and the duplicate we skipped.
    if verbose:
        print(f"Loaded {len(graph)} junctions and {len(roads)} distinct roads from {filename}")
        for a, b, m in duplicates:
            print(f"  Note: duplicate row ignored -> {a}, {b}, {m} (same road already listed)")
    return graph

"""This function turns our road list into the adjacency list, adding each road in both directions."""
def build_graph(roads: dict) -> dict:
    graph = {}
    for (a, b), minutes in roads.items():
        graph.setdefault(a, []).append((b, minutes))   # a can reach b
        graph.setdefault(b, []).append((a, minutes))   # and b can reach a, because roads are two-way
    return graph

"""This function returns a dictionary of {area name: the junction the area sits at}."""
def load_residential_areas(filename: str = "Q2_residential_areas.csv") -> dict:
    areas = {}
    with open(_path(filename), newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            areas[row["area"].strip()] = row["sits_at_junction"].strip()
    return areas

"""Each road shows up twice in the adjacency list (once from each end), so we divide by 2."""
def count_roads(graph: dict) -> int:
    return sum(len(neighbours) for neighbours in graph.values()) // 2

# ---------------------------------------------------------------- 3. The trap network

"""This function builds the trap network where greedy loses, with m areas around each side hub."""
def build_trap_network(m: int = 8) -> tuple[dict, dict]:
    if m < 2 or m % 2:
        raise ValueError("m must be an even number >= 2")
    roads = {}

    # West and East hubs, each with m junctions 5 minutes away.
    for i in range(1, m + 1):
        roads[("W" + str(i).zfill(2), "West")] = 5
        roads[("E" + str(i).zfill(2), "East")] = 5

    # Centre reaches half of each side in exactly 9 minutes (still counts as covered).
    for i in range(1, m // 2 + 1):
        roads[("Centre", "W" + str(i).zfill(2))] = 9
        roads[("Centre", "E" + str(i).zfill(2))] = 9

    # Centre's own village, so Centre covers one more area than the other hubs.
    roads[("Centre", "Centre village")] = 1

    # Every junction except the three hubs has a residential area on it.
    graph = build_graph(roads)
    areas = {j: j for j in graph if j not in ("West", "East", "Centre")}
    return graph, areas


 # Running this file on its own just prints the network so we can check it loaded properly.
if __name__ == "__main__":
    g = load_road_network(verbose=True)
    a = load_residential_areas()
    print(f"{len(a)} residential areas, {count_roads(g)} roads")
    for junction in sorted(g):
        print(f"  {junction}: {g[junction]}")

    rg, ra = generate_random_network(18, seed=1)
    tg, ta = build_trap_network(8)
    print(f"Random network: {len(rg)} junctions, {count_roads(rg)} roads | Trap network: {len(ta)} areas")