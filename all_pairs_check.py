NF = float("inf")
 
 
"""This function returns (dist, stats), where dist[a][b] is the shortest time from a to b."""
def floyd_warshall(graph: dict) -> tuple[dict, dict]:
    nodes = sorted(graph)

    ""This function returns (dist, stats), where dist[a][b] is the shortest time from a to b."""
def floyd_warshall(graph: dict) -> tuple[dict, dict]:
    nodes = sorted(graph)
    