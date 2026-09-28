NF = float("inf")
 
 
"""This function returns (dist, stats), where dist[a][b] is the shortest time from a to b."""
def floyd_warshall(graph: dict) -> tuple[dict, dict]:
    nodes = sorted(graph)

    """This function returns (dist, stats), where dist[a][b] is the shortest time from a to b."""
def all_pairs_check(graph: dict) -> tuple[dict, dict]:
    nodes = sorted(graph)

    # We start with 0 from a junction to itself and infinity everywhere else.
    dist = {a: {b: (0 if a == b else INF) for b in nodes} for a in nodes}


    for a in nodes:
        for b, minutes in graph[a]:
            dist[a][b] = min(dist[a][b], minutes)

    # For every junction k, we check if going through k makes any trip i to j faster.
    stats = {"inner_steps": 0}
    for k in nodes:
        for i in nodes:
            for j in nodes:
                stats["inner_steps"] += 1
                through_k = dist[i][k] + dist[k][j]
                if through_k < dist[i][j]:
                    dist[i][j] = through_k
    return dist, stats

# Running this file on its own prints one result and the step count (18^3 = 5832 on our data).
if __name__ == "__main__":
    from road_network import load_road_network
    d, s = floyd_warshall(load_road_network())
    print(f"Curepipe -> Pamplemousses: {d['Curepipe']['Pamplemousses']} minutes")
    print("Operation counts:", s)