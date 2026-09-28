import csv
import os
 
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

    return roads

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