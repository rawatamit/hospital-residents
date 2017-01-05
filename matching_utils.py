import graph
import copy
import collections

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
        M_u = M.get(u)
        # if u is not matched, return an empty list
        if M_u is None: return []
        # if u is matched, but has a single partner
        if not isinstance(M_u, set): return [M_u]
        # sort M_u according to u's preference list in G
        return sorted(M_u, key=G.E[u].index)

    # the least preferred resident this vertex is matched to
    def least_preferred_resident(ordered_residents):
        return ordered_residents[-1] if ordered_residents else None

    # does a prefer b over c
    def prefers(a, b, c):
        # a is unmatched in both
        if b is None and c is None: return False
        if b is None: return False  # false if b is None
        if c is None: return True  # true if c is None
        # check their relative ordering in a's pref list
        return G.E[a].index(b) < G.E[a].index(c)

    # mapping of hospitals to their least preferred neighbors in M
    least_preferred = dict((u, least_preferred_resident(order_residents(u))) for u in G.B)
    upairs = []  # unstable pairs
    for a in G.A:  # for each vertex in A
        # preference list for a
        pref_list = G.E[a]
        # we check all the pairs upto the matched partner of a
        # if it is not matched, check all the vertices in pref_list
        matched_partner_index = pref_list.index(M[a]) if a in M else len(pref_list)
        index = 0
        # while a prefers someone to its matched partner in pref_list
        while index < matched_partner_index:
            b = pref_list[index]
            # if b also prefers a to its least preferred partner
            if len(M[b]) < graph.upper_quota(G, b) or prefers(b, a, least_preferred[b]):
                upairs.append((a, b))  # this pair is unstable
            index += 1
    return upairs
