import graph
import collections
import random
import numpy as np
import matching_algos


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


def random_model_generator(n1, n2, k, max_capacity):
    """
    create a graph with the partition A of size n1
    and partition B of size n2 using the random model
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
   
    H= set('b{}'.format(i) for i in range(1, n2+1))

    # prepare a master list
    # master_list = list(h for h in H)
    # random.shuffle(master_list)

    # setup the capacities for the vertices
   
    capacities = dict((r, (0, 1)) for r in R)
    #capacities.update(dict((h, 1) for h in H))
    
    for h in H:
        #random_num_for_lowerQ  = random.randint((int)((3*max_capacity)/4), max_capacity)
        random_num_for_lowerQ = random.randint(0, max_capacity)
        
        capacities[h] = (random_num_for_lowerQ,max_capacity)

    
    pref_lists_H, pref_lists_R = collections.defaultdict(list), {}
    for resident in R:
        #min_val=random.randint((int)((3*len(H))/4), len(H))
        #pref_list = random.sample(H, min(min_val, k)) 
        pref_list = random.sample(H, min(len(H), k))  # random.randint(1, len(H)))  # sample houses
        pref_lists_R[resident] = pref_list  # order_by_master_list(pref_list, master_list)
        # add these residents to the preference list for the corresponding hospital
        for hospital in pref_list:
            pref_lists_H[hospital].append(resident)
            # random.shuffle(pref_lists_R[hospital])  # shuffle the preference list

    for hospital in H:
        random.shuffle(pref_lists_H[hospital])
    # create a dict with the preference lists for residents and hospitals
    E = pref_lists_R
    E.update(pref_lists_H)
    # only keep those hospitals which are in some residents preference list
    H_ = set(hospital for hospital in H if hospital in E)
    return graph.BipartiteGraph(R, H_, E, capacities)


def mahadian_k_model_generator_man_woman(n1, n2, k):
    """
    create a graph with the partition A of size n1 and
    partition B of size n2 using the model as described in
    Marriage, Honesty, and Stability
    Immorlica, Nicole and Mahdian, Mohammad
    Sixteenth Annual ACM-SIAM Symposium on Discrete Algorithms
    :param n1: size of partition A
    :param n2: size of partition B
    :param k: length of preference list for vertices in A
    :return: bipartite graph with above properties
    """
    # create the sets M and W, m_1 ... m_n1, w_1 .. w_n2
    M = list('m{}'.format(i) for i in range(1, n1+1))
    W = list('w{}'.format(i) for i in range(1, n2+1))

    # setup the capacities for the vertices
    capacities = dict((m, 1) for m in M)
    capacities.update(dict((w, 1) for w in W))

    # setup a probability distribution over the women
    p = np.random.random_sample((len(W),))
    # normalize the distribution
    p = p / np.sum(p)  # p is a ndarray, so this operation is perfectly fine

    pref_lists_W, pref_lists_M = collections.defaultdict(list), {}
    for m in M:
        # sample women according to the probability distribution and without replacement
        pref_lists_M[m] = list(np.random.choice(W, size=min(len(W), k), replace=False, p=p))
        # add these man to the preference list for the corresponding women
        for w in pref_lists_M[m]:
            pref_lists_W[w].append(m)

    for w in W:
        random.shuffle(pref_lists_W[w])
    # create a dict with the preference lists for men and women
    E = pref_lists_M
    E.update(pref_lists_W)
    # only keep those women which are in some man's preference list
    W_ = set(w for w in W if w in E)
    return graph.BipartiteGraph(M, W_, E, capacities)


def mahadian_k_model_generator_hospital_residents(n1, n2, k, cap):
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
    
    for h in H:
        random_num_for_lowerQ = random.randint(0, cap)
        #random_num_for_lowerQ = random.randint(0, max_capacity)
        capacities[h] = (random_num_for_lowerQ,cap)


    # setup a probability distribution over the hospitals
    p = np.random.geometric(p=0.10, size=len(H))
    # normalize the distribution
    p = p / np.sum(p)  # p is a ndarray, so this operation is perfectly fine
    #print('n1 = {}, n2={}, k={}, p={}'.format(n1, n2, k, p))

    pref_lists_H, pref_lists_R = collections.defaultdict(list), {}
    for r in R:
        #min_val=random.randint((int)((3*len(H))/4), len(H))
        # sample women according to the probability distribution and without replacement
        pref_lists_R[r] = list(np.random.choice(H, size=min(len(H), k), replace=False, p=p))
        # add these man to the preference list for the corresponding women
        for h in pref_lists_R[r]:
            pref_lists_H[h].append(r)

    for h in H:
        pref_lists_H[h] = order_by_master_list(pref_lists_H[h], master_list)
        # random.shuffle(pref_lists_H[h])
    # create a dict with the preference lists for residents and hospitals
    E = pref_lists_R
    E.update(pref_lists_H)
    # only keep those hospitals which are in some resident's preference list
    H_ = set(h for h in H if h in E)
    return graph.BipartiteGraph(R, H_, E, capacities)


def NRcheck(G):
        sum=0
        
        for h in G.B:
            sum+=graph.lower_quota(h,G)
        return len(G.A)>=sum


def checkForLQHosp(G):
	for h in G.B:
	    if graph.lower_quota(h,G)>0:
                if len(G.E[h])!=len(G.A) :
                    
                    return False
	return True


def feasibility_check(G):
        G1 = graph.copy_graph(G)
        #G = mahadian_k_model_generator_hospital_residents(n1, n2, k, max_capacity)
        
        for h in G.B:
             if graph.lower_quota(G, h)==0:
                   G1.B.remove(h)
                   
                   for r in G.E[h]:
                          G1.E[r].remove(h)
                   del G1.E[h]
                   del G1.capacities[h]
             else:
                   G1.capacities[h] = (graph.lower_quota(G, h), graph.lower_quota(G, h))
        #print("---------- G1-----------\n")
        #print(G1)
        #print("---------- G-----------\n")
        #print(G)
        #print("-------------max_card_mat----------\n")
        
        Max_M = matching_algos.max_card_hospital_residents(graph.copy_graph(G1))
        #print(graph.to_easy_format(G1, Max_M))
      
        if check_on_max_card_matching(G1, Max_M):
            M = matching_algos.stable_matching_hospital_residents(graph.copy_graph(G))
            #print("-------------stable_mat----------\n")
            #print(graph.to_easy_format(G, M))
            for h in G.B:
                if h not in M:
                    if graph.lower_quota(G, h)>0:
                        return True
                else:
                    if len(M[h])<graph.lower_quota(G,h):
                        return True
            return False
 
        else: 
            return False


def check_on_max_card_matching(G1, M):
        for h in G1.B:
             if len(M[h])!=graph.lower_quota(G1, h):
                   return False
        return True


def main():
    import sys
    if len(sys.argv) < 5:
        print("usage: {} <n1> <n2> <k> <max capacity>".format(sys.argv[0]), file=sys.stderr)
    else:
        n1, n2, k, max_capacity = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        # G = random_model_generator(n1, n2, k, max_capacity)
        G = mahadian_k_model_generator_hospital_residents(n1, n2, k, max_capacity)
        #print(feasibility_check(G))
        while feasibility_check(G)==False:
            #print("False")
            # G = random_model_generator(n1, n2, k, max_capacity)
            G = mahadian_k_model_generator_hospital_residents(n1, n2, k, max_capacity)
        
        print(graph.graph_to_UTF8_string(G), file=sys.stdout)
        
      #  print(graph.graph_to_UTF8_string(G), file=sys.stdout)
      #  sum_of_lower_quotas=0
      #  for h in G.B:
      #          sum_of_lower_quotas+=graph.lower_quota(h,G)
	
 #       print("count of generation : ",countofgen)


if __name__ == '__main__':
    main()
