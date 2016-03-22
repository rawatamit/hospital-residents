import graph
import collections
import random


def random_sample(G):
    """
    generates a random sampling, which is then returned
    as a bipartite graph, from the given graph
    the returned preference lists are symmetric
    :param G: bipartite graph
    :return: bipartite graph from a random sample
    """
    def order_by_master_list(l, master_list):
        return sorted(l, key=master_list.index)

    # prepare a master list
    master_list = list(h for h in G.B)
    random.shuffle(master_list)

    E = collections.defaultdict(list)  # to store the new sampled preference list
    for resident in G.A:
        pref_list = G.E[resident]
        E[resident] = order_by_master_list(pref_list[:], master_list)
        # for all the hospitals add the students to their preference list
        for hospital in pref_list:
            E[hospital].append(resident)

    # shuffle the preference list for the hospitals
    for hospital in G.B:
        random.shuffle(E[hospital])

    return graph.BipartiteGraph(G.A, G.B, E, G.capacities)


def generate_random_graph(n1, n2, k, max_capacity):
    """
    create a graph with the partition A of size n1
    and partition B of size n2
    :param n1: size of partition A
    :param n2: size of partition B
    :param k: length of preference list for vertices in A
    :param max_capacity: maximum capacity a vertex in partition B can have
    :return: bipartite graph with above properties
    """
    def order_by_master_list(l, master_list):
        return sorted(l, key=master_list.index)

    # create the sets R and H, r_1 ... r_n1, h_1 .. h_n2
    R = set('a{}'.format(i) for i in range(1, n1+1))
    H = set('b{}'.format(i) for i in range(1, n2+1))

    # prepare a master list
    master_list = list(h for h in H)
    random.shuffle(master_list)

    # setup the capacities for the vertices
    capacities = dict((r, 1) for r in R)
    capacities.update(dict((h, 1) for h in H))
    # capacities.update(dict((h, random.randint(1, max_capacity)) for h in H))

    pref_listsH, pref_listsR = collections.defaultdict(list), {}
    for resident in R:
        pref_list = random.sample(H, k)  # random.randint(1, len(H)))  # sample houses
        pref_listsR[resident] = order_by_master_list(pref_list, master_list)  # pref_list
        # add these residents to the preference list for the corresponding hospital
        for hospital in pref_list:
            pref_listsH[hospital].append(resident)
            # random.shuffle(pref_listsR[hospital])  # shuffle the preference list

    """
    pref_listsH, pref_listsR = collections.defaultdict(list), {}
    for resident in R:
        pref_list = random.sample(H, k)  # sample k houses
        pref_listsR[resident] = pref_list
        # add these residents to the preference list for the corresponding hospital
        for hospital in pref_list:
            pref_listsH[hospital].append(resident)
        # random.shuffle(pref_listsR[hospital])  # shuffle the preference list
    """

    for hospital in H:
        random.shuffle(pref_listsH[hospital])
    # create a dict with the preference lists for residents and hospitals
    E = pref_listsR
    E.update(pref_listsH)
    # only keep those hospitals which are in some residents preference list
    H_ = set(hospital for hospital in H if hospital in E)
    return graph.BipartiteGraph(R, H_, E, capacities)


def main():
    import sys
    if len(sys.argv) < 5:
        print("usage: {} <n1> <n2> <k> <max capacity>".format(sys.argv[0]), file=sys.stderr)
    else:
        n1, n2, k, max_capacity = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        G = generate_random_graph(n1, n2, k, max_capacity)
        print(graph.graph_to_UTF8_string(G), file=sys.stdout)

if __name__ == '__main__':
    main()
