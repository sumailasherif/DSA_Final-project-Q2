"""These are our correctness checks, we run them before any timing (same idea as in our sorting coursework)."""
from itertools import combinations
from math import comb

from road_network import (load_road_network, load_residential_areas, build_graph, count_roads,
                          generate_random_network, build_trap_network)
from shortest_paths import dijkstra, fastest_route, road_times_along, fewest_roads_route, all_pairs_check
from stop_placement import build_coverage, areas_covered_by, greedy_place_stops, exhaustive_best_stops

"""This checks the data loaded properly: 18 junctions, 24 roads (after the duplicate), 18 areas, two-way roads."""
def test_loading() -> None:
    g, a = load_road_network(), load_residential_areas()
    assert len(g) == 18, "expected 18 junctions"
    assert count_roads(g) == 24, "25 rows minus the duplicated Moka-St Pierre road = 24 roads"
    assert len(a) == 18 and set(a.values()) <= set(g), "every area must sit at a real junction"
    assert all(b in [n for n, _ in g[a_]] for a_ in g for b, _ in g[a_]), "roads must be two-way"

"""This checks Dijkstra against Floyd-Warshall (all_pairs_check) on every pair, on the real network and 15 random ones."""
def test_dijkstra_matches_all_pairs_check() -> None:
    graphs = [load_road_network()] + [generate_random_network(v, seed=s)[0] for v in (5, 10, 20) for s in range(5)]
    for g in graphs:
        fw, _ = all_pairs_check(g)
        for source in g:
            dist, _, _ = dijkstra(g, source)
            for target in g:
                assert dist[target] == fw[source][target], f"{source}->{target} disagrees"

"""This checks the route is 59 minutes, the road times add up, and going back takes the same time."""
def test_fastest_route() -> None:
    g = load_road_network()
    path, minutes, _ = fastest_route(g, "Curepipe", "Pamplemousses")
    assert minutes == 59
    assert path[0] == "Curepipe" and path[-1] == "Pamplemousses"
    assert sum(road_times_along(g, path)) == minutes, "route legs must add up to the total"
    route_back, minutes_back, _ = fastest_route(g, "Pamplemousses", "Curepipe")
    assert minutes_back == minutes, "two-way roads: same time in both directions"

    """This checks that stopping Dijkstra at 9 minutes gives the same coverage with fewer relaxations."""
def test_cutoff_gives_same_coverage() -> None:
    cases = [(load_road_network(), load_residential_areas())]
    cases += [generate_random_network(v, seed=s) for v in (8, 18, 30) for s in range(5)]
    for g, a in cases:
        with_cutoff, s1 = build_coverage(g, a, use_cutoff=True)
        without, s2 = build_coverage(g, a, use_cutoff=False)
        assert with_cutoff == without
        assert s1["relaxations"] <= s2["relaxations"]

        """This checks the boundary: exactly 9 minutes counts, 10 does not, and 4 + 5 over two roads counts too."""
def test_exactly_nine_counts() -> None:
    nine = build_graph({("A", "B"): 9})
    ten = build_graph({("A", "B"): 10})
    two_roads = build_graph({("A", "M"): 4, ("M", "B"): 5})       # 4 + 5 = 9 minutes through a middle junction
    areas = {"Area B": "B"}
    assert "Area B" in build_coverage(nine, areas)[0]["A"], "exactly 9 minutes must count"
    assert "Area B" not in build_coverage(ten, areas)[0]["A"], "10 minutes must not count"
    assert "Area B" in build_coverage(two_roads, areas)[0]["A"], "9 minutes over two roads must count"


"""This checks that when two junctions tie, greedy picks the one that comes first alphabetically."""
def test_alphabetical_tie_break() -> None:
    coverage = {"Zebra": frozenset({"x", "y"}), "Alpha": frozenset({"p", "q"}), "Mid": frozenset({"x"})}
    stops, _, log, _ = greedy_place_stops(coverage, 1)
    assert stops == ["Alpha"], "a tie must go to the alphabetically first name"
    assert log[0]["tied_with"] == ["Zebra"]

"""This checks our real answers: greedy's six stops cover 17, the best six cover 18, from 18,564 sets."""
def test_supplied_answers() -> None:
    g, a = load_road_network(), load_residential_areas()
    cov, _ = build_coverage(g, a)
    stops, covered, _, _ = greedy_place_stops(cov, 6)
    assert stops == ["Quatre Bornes", "Arsenal", "Curepipe", "Ebene", "Moka", "Pailles"]
    assert len(covered) == 17
    best, n, s = exhaustive_best_stops(cov, a, 6)
    assert n == 18 and s["subsets_evaluated"] == comb(18, 6) == 18564
    assert len(areas_covered_by(best, cov)) == n, "reported set must really cover n areas"

    """This checks greedy is never better than exhaustive, and with only one stop they must be equal."""
def test_greedy_never_beats_exhaustive() -> None:
    for v in (8, 12, 16):
        for seed in range(10):
            g, a = generate_random_network(v, seed=seed)
            cov, _ = build_coverage(g, a)
            for k in (1, 2, 3, 4):
                _, gc, _, _ = greedy_place_stops(cov, k)
                _, n, _ = exhaustive_best_stops(cov, a, k)
                assert len(gc) <= n
                if k == 1:
                    assert len(gc) == n, "with one stop, greedy IS exhaustive"

"""This checks our bitmask shortcut gives the same best answer as a slow search using normal sets."""
def test_bitmask_search_matches_plain_sets() -> None:
    for seed in range(5):
        g, a = generate_random_network(12, seed=seed)
        cov, _ = build_coverage(g, a)
        for k in (2, 3, 4):
            slow = max(len(areas_covered_by(c, cov)) for c in combinations(sorted(cov), k))
            _, fast, _ = exhaustive_best_stops(cov, a, k)
            assert slow == fast

"""This checks the trap network: greedy picks Centre with no tie, gets 13, and the best (East + West) gets 16."""
def test_counterexample() -> None:
    g, a = build_trap_network(8)
    cov, _ = build_coverage(g, a)
    gs, gc, log, _ = greedy_place_stops(cov, 2)
    es, n, _ = exhaustive_best_stops(cov, a, 2)
    assert gs[0] == "Centre" and log[0]["tied_with"] == [], "round 1 is a clear win, not a tie"
    assert (len(gc), n) == (13, 16)
    assert sorted(es) == ["East", "West"]

"""This checks BFS finds a 6-road route that is slower than Dijkstra's 8-road, 59-minute route."""
def test_bfs_fewest_roads() -> None:
    g = load_road_network()
    path = fewest_roads_route(g, "Curepipe", "Pamplemousses")
    fast, _, _ = fastest_route(g, "Curepipe", "Pamplemousses")
    assert len(path) - 1 == 6 and len(fast) - 1 == 8
    assert sum(road_times_along(g, path)) > 59

    # The list of all our checks, run in this order.
TESTS = [test_loading, test_dijkstra_matches_all_pairs_check, test_fastest_route,
         test_cutoff_gives_same_coverage, test_exactly_nine_counts, test_alphabetical_tie_break,
         test_supplied_answers, test_greedy_never_beats_exhaustive,
         test_bitmask_search_matches_plain_sets, test_counterexample, test_bfs_fewest_roads]

"""This function runs every check, prints PASS or FAIL for each, and returns True only if all passed."""
def run_correctness_checks() -> bool:
    passed = 0
    for test in TESTS:
        try:
            test()
            print(f"  PASS  {test.__name__}")
            passed += 1
        except AssertionError as error:
            print(f"  FAIL  {test.__name__}: {error}")
    print(f"{passed}/{len(TESTS)} checks passed.")
    return passed == len(TESTS)
if __name__ == "__main__":
    run_correctness_checks()

    