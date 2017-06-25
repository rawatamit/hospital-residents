import graph
import collections
import random
import numpy as np


def random_model_generator(n1, n2, k, cap):
    """
    create a graph with the partition A of size n1
    and partition B of size n2 using the random model
    :param n1: size of partition A
    :param n2: size of partition B
    :param k: length of preference list for vertices in A
    :param cap: capacity of a vertex in partition B
    :return: bipartite graph with above properties
    """
    def order_by_master_list(l, master_list):
        return sorted(l, key=master_list.index)

    # create the sets R and H, r_1 ... r_n1, h_1 .. h_n2
    R = set('r{}'.format(i) for i in range(1, n1+1))
    H = set('h{}'.format(i) for i in range(1, n2+1))

    # prepare a master list
    # master_list = list(h for h in H)
    # random.shuffle(master_list)

    # setup the capacities for the vertices
    capacities = dict((r, (0, 1)) for r in R)
    #capacities.update(dict((h, 1) for h in H))
    capacities.update(dict((h, (0, cap)) for h in H))

    pref_lists_H, pref_lists_R = collections.defaultdict(list), {}
    for resident in R:
        pref_list = random.sample(H, min(len(H), k))  # random.randint(1, len(H)))  # sample houses
        pref_lists_R[resident] = pref_list  # order_by_master_list(pref_list, master_list)
        # add these residents to the preference list for the corresponding hospital
        for hospital in pref_list:
            pref_lists_H[hospital].append(resident)

    for hospital in H:
        random.shuffle(pref_lists_H[hospital])

    # create a dict with the preference lists for residents and hospitals
    E = pref_lists_R
    E.update(pref_lists_H)

    # only keep those hospitals which are in some residents preference list
    H_ = set(hospital for hospital in H if hospital in E)
    return graph.BipartiteGraph(R, H_, E, capacities)


def mahadian_model_generator(n1, n2, k, cap):
    """
    create a graph with the partition R of size n1 and
    partition H of size n2 using the model as described in
    Marriage, Honesty, and Stability
    Immorlica, Nicole and Mahdian, Mohammad
    Sixteenth Annual ACM-SIAM Symposium on Discrete Algorithms
    :param n1: size of partition R
    :param n2: size of partition H
    :param k: length of preference list for the residents
    :param cap: capacity of the hospitals
    :return: bipartite graph with above properties
    """
    def order_by_master_list(l, master_list):
        return sorted(l, key=master_list.index)

    # create the sets R and H, r_1 ... r_n1, h_1 .. h_n2
    R = list('r{}'.format(i) for i in range(1, n1+1))
    H = list('h{}'.format(i) for i in range(1, n2+1))

    # prepare a master list
    master_list = list(r for r in R)
    random.shuffle(master_list)

    # setup the capacities for the vertices
    capacities = dict((r, (0, 1)) for r in R)
    capacities.update(dict((h, (0, cap)) for h in H))

    # setup a probability distribution over the hospitals
    p = np.random.geometric(p=0.10, size=len(H))

    # normalize the distribution
    p = p / np.sum(p)  # p is a ndarray, so this operation is correct

    prob_dict = dict(zip(H, p))
    master_list_h = sorted(H, key=lambda h: prob_dict[h], reverse=True)
    # print(prob_dict, master_list_h, sep='\n')

    pref_H, pref_R = collections.defaultdict(list), {}
    for r in R:
        # sample women according to the probability distribution and without replacement
        pref_R[r] = list(np.random.choice(H, size=min(len(H), k), replace=False, p=p))
        # add these man to the preference list for the corresponding women
        for h in pref_R[r]:
            pref_H[h].append(r)

    for r in R:
        pref_R[r] = order_by_master_list(pref_R[r], master_list_h)

    for h in H:
        pref_H[h] = order_by_master_list(pref_H[h], master_list)
        #random.shuffle(pref_H[h])

    # create a dict with the preference lists for residents and hospitals
    E = pref_R
    E.update(pref_H)

    # only keep those hospitals which are in some resident's preference list
    H_ = set(h for h in H if h in E)
    return graph.BipartiteGraph(R, H_, E, capacities)


def main():
    import sys
    if len(sys.argv) < 6:
        print("usage: {} <n1> <n2> <k> <capacity> <output_path>".format(sys.argv[0]), file=sys.stderr)
    else:
        n1, n2, k, max_capacity = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        output_path = sys.argv[5]
        G = mahadian_model_generator(n1, n2, k, max_capacity)
        # G = random_model_generator(n1, n2, k, max_capacity)
        with open(output_path, encoding='utf-8', mode='w') as out:
            out.write(graph.graph_to_UTF8_string(G))

if __name__ == '__main__':
    main()
