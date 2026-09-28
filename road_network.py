"""Loads the supplied road network and residential area data. This is pure file reading and data structuring, not part of the
algorithmic core, so it's fair scaffolding to hand you ready-made."""
import csv
def load_road_network(filename: str = "Q2_road_network.csv") -> dict:
    graph = {}
    with open(filename, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            a, b, minutes = row["from"], row["to"], int(row["minutes"])
            graph.setdefault(a, []).append((b, minutes))
            graph.setdefault(b, []).append((a, minutes))
    return graph

    def load_residential_areas(filename: str = "Q2_residential_areas.csv") -> dict: areas = {}
    with open(filename, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            areas[row["area"]] = row["sits_at_junction"]
    return areas
