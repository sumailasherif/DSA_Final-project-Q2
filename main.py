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


 """This function runs our Dijkstra and then prints the fastest route road by road, with the operation counts."""
 def show_fastest_route(graph: dict) -> None:
   path, minutes, stats = fastest_route(graph, START, END)
    print(f"\nFastest route {START} -> {END}: {minutes} minutes over {len(path) - 1} roads")
    for (a, b), m in zip(zip(path, path[1:]), road_times_along(graph, path)):
        print(f"  {a:14} -> {b:16} {m:3} min")
    print(f"  Dijkstra did {stats['relaxations']} relaxations, {stats['pops']} heap pops "
          f"({stats['stale_pops']} stale), {stats['edge_checks']} edge checks")