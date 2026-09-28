NF = float("inf")
 
 
"""This function returns (dist, stats), where dist[a][b] is the shortest time from a to b."""
def floyd_warshall(graph: dict) -> tuple[dict, dict]:
    nodes = sorted(graph)

    """This function returns (dist, stats), where dist[a][b] is the shortest time from a to b."""
def all_pairs_check(graph: dict) -> tuple[dict, dict]:
    nodes = sorted(graph)

    # We start with 0 from a junction to itself and infinity everywhere else.
    dist = {a: {b: (0 if a == b else INF) for b in nodes} for a in nodes}
 