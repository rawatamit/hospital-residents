import graph
import collections
import random


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
    # create the sets R and H, r_1 ... r_n1, h_1 .. h_n2
    R = set('a{}'.format(i) for i in range(1, n1+1))
    H = set('b{}'.format(i) for i in range(1, n2+1))

    capacities = dict((r, 1) for r in R)
    capacities.update(dict((h, random.randint(1, max_capacity)) for h in H))

    pref_listsH, pref_listsR = collections.defaultdict(list), {}
    for resident in R:
        pref_list = random.sample(H, k)  # sample k houses
        pref_listsR[resident] = pref_list
        # add these residents to the preference list for the corresponding hospital
        for hospital in pref_list:
            pref_listsH[hospital].append(resident)
        # random.shuffle(pref_listsR[hospital])  # shuffle the preference list

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
