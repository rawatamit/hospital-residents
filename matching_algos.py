import graph
import matching_utils
import copy
import heapq
import collections
import networkx


def max_card_man_woman(G):
    """
    computes maximum cardinality matching in a bipartite graph,
    :param G: bipartite graph
    :return: maximum cardinality matching in G
    """
    G_nx = graph.to_networkx_graph(G)
    M = networkx.bipartite.maximum_matching(G_nx)
    M_max_card = dict((h, M[h]) for h in G.B if h in M)
    M_max_card.update(dict((r, M[r]) for r in G.A if r in M))
    return M_max_card


def max_card_hospital_residents(G):
    """
    computes maximum cardinality matching in a bipartite graph,
    :param G: bipartite graph
    :return: maximum cardinality matching in G
    """
    G_, reverse_copies = matching_utils.blow_instance(G)
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


def popular_matching_man_woman(G):
    """
    computes popular matching in a bipartite graph,
    where man and woman have preferences on each other
    :param G: bipartite graph
    :return: popular matching in G
    """
    G_ = matching_utils.augment_graph(G)
    M = stable_matching_man_woman(G_)
    return matching_utils.to_standard_format(M)


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
            if len(M[h]) >= graph.upper_quota(G, h):  # h is fully subscribed
                _, r_ = heapq.heappop(M[h])  # worst resident assigned to h
                free_list.append(r_)  # assign r_ to be free
            heapq.heappush(M[h], (get_rank(h, r, rank_map), r))  # assign r to h
            if len(M[h]) >= graph.upper_quota(G, h):  # h is fully subscribed
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
    G_ = matching_utils.augment_graph(G)
    M = stable_matching_hospital_residents(G_)
    return matching_utils.to_standard_format(M)
