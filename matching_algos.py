import graph
import graph_parser
import copy
import heapq
import collections
import networkx

Vertex = collections.namedtuple('Vertex', ['id', 'level'])


def blow_house_instances(G):
    """
    create copies for the vertices in G.B
    :param G: bipartite graph
    :return: dict containing copies for all the vertices,
             another dict containing information a "reverse"
             map to conveniently find the original house
             given such a copy
    """
    def create_copies(h, cap):
        """
        create virtual copies for h
        does not modify G
        :param h: house
        :param cap: capacity
        :return: set with cap copies for h
        """
        return list('{}@{}'.format(h, i) for i in range(cap))

    # store the copies for h
    copies = dict((h, create_copies(h, G.capacities[h])) for h in G.B)
    reverse_copies = dict((h_copy, h) for h in G.B for h_copy in copies[h])
    return copies, reverse_copies


def blow_instance(G):
    """
    blow the bipartite graph G, by creating k copies
    for a vertex in G.B, where k is its capacity
    also correctly set the preference list for the
    vertices for the vertices in this blown up instance
    :param G: bipartite graph
    :return: blown up instance G'
    """
    copies, reverse_copies = blow_house_instances(G)
    # partition B now contains houses with copies of the instance
    B = set(h_copy for h in G.B for h_copy in copies[h])

    # all the houses and residents now have a capacity of 1
    capacities = dict((h, 1) for h in B)
    capacities.update(dict((r, 1) for r in G.A))

    # fix all the edges in the new graph
    E = collections.defaultdict(list)
    for r in G.A:
        for h_orig in G.E[r]:
            for h_copy in copies[h_orig]:
                E[r].append(h_copy)
                E[h_copy] = G.E[h_orig][:]

    return graph.BipartiteGraph(G.A, B, E, capacities), reverse_copies


def max_card_matching(G):
    """
    computes maximum cardinality matching in a bipartite graph,
    :param G: bipartite graph
    :return: maximum cardinality matching in G
    """
    G_, reverse_copies = blow_instance(G)
    G_nx = graph.to_networkx_graph(G_)
    M = networkx.bipartite.maximum_matching(G_nx)
    M_max_card = collections.defaultdict(set)
    for h in G_.B:
        if h in M:
            M_max_card[reverse_copies[h]].add(M[h])
    M_max_card.update(dict((r, reverse_copies[M[r]]) for r in G.A if r in M))
    return M_max_card


def stable_matching_man_woman(G):
    """
    computes stable matching in a bipartite graph,
    where man and woman have preferences on each other
    :param G: bipartite graph
    :return: man optimal stable matching
    """
    # mark all men (by pushing into the free_list) and women (implicitly) free
    # free_list behaves like a stack
    M, free_list = {}, [m for m in G.A]

    while free_list:  # while free_list is not empty
        m = free_list.pop()  # remove a man from free_list
        if G.E[m]:  # if m's pref list is not empty
            w = G.E[m][0]  # w is the most preferred woman for m
            if w in M:  # if w is matched
                free_list.append(M[w])  # add M[w] to free_list
            M[w] = m  # accept proposal from m
            graph.update_pref_lists(m, w, G.E, G.E)

    # add partners for a to M
    M.update(dict((a, b) for b, a in M.items()))
    return M


def dummy_hospital(r):
    """
    dummy hospital w.r.t resident r
    :param r: resident
    :return: dummy hospital d(r)
    """
    return 'd({})'.format(r)


def preflist_resident(r, G):
    """
    creates preference list for resident r
    in the augmented graph G'
    :param r: resident
    :param G: original bipartite graph
    :return: preference list for r in G
    """
    # for a level 0 resident its preference list is the same
    # as r followed by d(r)
    # for a level 1 resident its preference list is d(r) followed
    # followed by original preference list for r
    preflist = []
    if r.level == 1:
        preflist.append(dummy_hospital(r.id))
    preflist.extend(G.E[r.id])
    if r.level == 0:
        preflist.append(dummy_hospital(r.id))
    return preflist


def preflist_dummy(d):
    """
    generate preference list for dummy hospital d
    :param d: dummy hospital
    :return: preference list for d
    """
    return [Vertex(d, 0), Vertex(d, 1)]


def preflist_hospital(h, G):
    """
    creates preference list for hospital h
    in the augmented graph G'
    :param h: hospital
    :param G: original bipartite graph
    :return: preference list for h in G
    """
    preflist = [Vertex(r, 1) for r in G.E[h]]
    for r in G.E[h]:
        preflist.append(Vertex(r, 0))
    return preflist


def augment_graph(G):
    """
    create graph G' as described in KavAgnes2015
    :param G: bipartite graph G
    :return: augmented graph G'
    """
    # corresponding to every man a \in A, two men a_0 and a_1 in A'
    # and one woman d(a) in B'
    A_ = set(Vertex(r, 0) for r in G.A) | set(Vertex(r, 1) for r in G.A)
    dummies = set(dummy_hospital(r) for r in G.A)  # dummy women
    B_ = G.B | dummies
    capacities = copy.copy(G.capacities)  # capacities for new graph
    # dummy vertices have capacity 1
    capacities.update(dict((dummy, 1) for dummy in dummies))
    # add preference list for the residents
    E_ = dict((r, preflist_resident(r, G)) for r in A_)
    # preference list for the dummies
    E_.update(dict((dummy_hospital(r), preflist_dummy(r)) for r in G.A))
    # preference list for hospital
    E_.update(dict((h, preflist_hospital(h, G)) for h in G.B))
    return graph.BipartiteGraph(A_, B_, E_, capacities)


def to_standard_format(M):
    """
    create a dict such that the matched partner(s)
    of a vertex u can be obtained simply by accessing M[u]
    :param M: matching
    :return: matching in standard format
    """
    def is_dummy(u):
        return isinstance(u, str) and u.startswith('d(')

    def get_id(u):
        return u if isinstance(u, str) else u.id

    def partners(M_u):
        return set(map(get_id, M_u)) if isinstance(M_u, set) else get_id(M_u)

    # remove all the dummy vertices
    M_ = dict((u, M[u]) for u in M if not is_dummy(u) and not is_dummy(M[u]))
    M_ = dict((get_id(u), partners(M[u])) for u in M_)
    return M_


def popular_matching_man_woman(G):
    """
    computes popular matching in a bipartite graph,
    where man and woman have preferences on each other
    :param G: bipartite graph
    :return: popular matching in G
    """
    G_ = augment_graph(G)
    M = stable_matching_man_woman(G_)
    return to_standard_format(M)


def get_rank(h, r, rank_map):
    """
    heapq provides a min heap implementation
    but the higher ranked vertices are lower
    priority, fix this by subtracting the rank
    of the vertex by the length of the pref list
    :param h: house
    :param r: resident
    :param rank_map: dict containing preference list of h
    :return: rank of r in h's preference list
    """
    return len(rank_map[h]) - rank_map[h].index(r)


def unstable_pairs(G, M):
    """
    finds the unstable pairs in G w.r.t matching M,
    hospital residents instance
    :param G: bipartite graph
    :param M: matching in G
    :return: list of the unstable pairs
    """
    # order residents according to u's preference list
    def order_residents(u):
        # TODO: need to make this a bit more robust
        if u in M:  # only if u is matched to someone
            # check if M[u] is a string,
            # if yes return the matched partner wrapped in a list
            # if no then sort them according to u's preference list in G
            # this takes care of both the man-woman and hospital residents case
            return [M[u]] if isinstance(M[u], str) else sorted(M[u], key=G.E[u].index)
        else:  # u is not matched in M, return an empty list
            return []

    # the least preferred resident this vertex is matched to
    def least_preferred_resident(ordered_residents):
        n = len(ordered_residents)
        return ordered_residents[n-1] if ordered_residents else None

    # does a prefer b over c
    def prefers(a, b, c):
        if c is None: return True  # true if c is None
        if b is None: return False  # false if b is None
        # check their relative ordering in a's pref list
        return G.E[a].index(b) < G.E[a].index(c)

    # mapping of hospitals to their least preferred neighbors in M
    least_preferred = dict((u, least_preferred_resident(order_residents(u))) for u in G.B)
    upairs = []  # unstable pairs
    for a in G.A:  # for each vertex in A
        index, partner, pref_list = 0, M.get(a), G.E[a]
        # while a prefers a woman to its matched partner in its pref list
        while index < len(pref_list) and prefers(a, pref_list[index], partner):
            b = pref_list[index]
            # if b also prefers a to its least preferred partner
            if prefers(b, a, least_preferred[b]):
                upairs.append((a, b))  # this pair is unstable
            index += 1
    return upairs


def stable_matching_hospital_residents(G):
    """
    computes stable matching in a bipartite graph,
    where residents and hospitals have preferences on each other
    :param G: bipartite graph
    :return: resident optimal stable matching
    """
    # free_list behaves like a stack
    M = dict((h, []) for h in G.B)  # assign all hospitals to be totally unsubscribed
    free_list = [r for r in G.A]  # assign all resident to be free
    rank_map = copy.deepcopy(G.E)  # we will be modifying G.E, so make a copy

    while free_list:  # while free_list is not empty
        r = free_list.pop()  # remove a resident from free_list
        if G.E[r]:  # if r's pref list is not empty
            h = G.E[r][0]  # first hospital on r's list
            if len(M[h]) >= G.capacities[h]:  # h is fully subscribed
                _, r_ = heapq.heappop(M[h])  # worst resident assigned to h
                free_list.append(r_)  # assign r_ to be free
            heapq.heappush(M[h], (get_rank(h, r, rank_map), r))  # assign r to h
            if len(M[h]) >= G.capacities[h]:  # h is fully subscribed
                _, s = M[h][0]  # worst resident provisionally assigned to h
                graph.update_pref_lists(s, h, G.E, G.E)

    # return the matching in a tuple form
    M_ = dict((r, h) for h in M for _, r in M[h])
    M_.update(dict((h, set(r for _, r in M[h])) for h in M if M[h]))
    return M_


def popular_matching_hospital_residents(G):
    """
    computes popular matching in a bipartite graph,
    where residents and hospitals have preferences on each other
    :param G: bipartite graph
    :return: popular matching in G
    """
    G_ = augment_graph(G)
    M = stable_matching_hospital_residents(G_)
    return to_standard_format(M)


def main():
    import sys
    if len(sys.argv) < 2:
        print('usage: {} <graph file>'.format(sys.argv[0]))
    else:
        G = graph_parser.read_graph(sys.argv[1])
        G_man = graph.copy_graph(G)
        print('man optimal stable matching:', stable_matching_man_woman(G_man))
        G_woman = graph.copy_graph(graph.BipartiteGraph(G.B, G.A, G.E, G.capacities))
        _, M_man = popular_matching_man_woman(G_man)
        print('man proposing popular matching:', M_man)
        graph.print_graph(G_man, sys.stdout)
        _, M_woman = popular_matching_man_woman(G_woman)
        print('woman proposing popular matching:', M_woman)
        graph.print_graph(G_woman, sys.stdout)
        #graph.to_graphviz(G, M_, sys.stdout)

if __name__ == '__main__':
    main()
