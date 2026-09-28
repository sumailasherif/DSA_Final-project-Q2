import sys
from math import comb
 
from road_network import load_road_network, load_residential_areas, count_roads
from dijkstra import fastest_route, road_times_along
from coverage import build_coverage, COVER_LIMIT

 """The two ends of our new bus route."""
START, END = "Curepipe", "Pamplemousses"

 """This function prints every junction and the roads that leaves it, so we can see the whole network of roads."""
def show_network(graph: dict, areas: dict) -> None:
    print(f"\n{len(graph)} junctions, {count_roads(graph)} two-way roads, {len(areas)} residential areas")
    for junction in sorted(graph):
        roads = ", ".join(f"{n} ({m} min)" for n, m in sorted(graph[junction]))
        print(f"  {junction:16} -> {roads}")
 