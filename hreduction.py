import graph
import graph_parser
import sys
import collections


def hreduction(G):
    for r in G.A:
        pref_list = []
        for h in G.E[r]:
            if graph.lower_quota(G, h) > 0:
                pref_list.append(h)
        G.E[r] = pref_list

    B = set(h for h in G.B if graph.lower_quota(G, h) > 0)
    for h in B:
        G.capacities[h] = (0, graph.lower_quota(G, h))
    return graph.BipartiteGraph(G.A, B, G.E, G.capacities)


def main():
    G = graph_parser.read_graph(sys.argv[1])
    G1 = hreduction(graph.copy_graph(G))
    print(graph.graph_to_UTF8_string(G1))

if __name__ == '__main__':
    main()
