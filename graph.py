import collections
import networkx as nx

BipartiteGraph = collections.namedtuple('BipartiteGraph', ['A', 'B', 'E', 'capacities'])


def make_graph(A, B, pref_listsA, pref_listsB, capacities):
    """
    creates a graph given partitions A, B, and
    the preference lists which are in the format
    [(v, [pref_list]), ...]
    :param A: partition A
    :param B: partition B
    :param pref_listsA: preference lists for vertices in A
    :param pref_listsB: preference lists for vertices in B
    :param capacities: capacities for the vertices in A U B
    :return: bipartite graph with vertices A U B,
             and preference lists as specified
    """
    E = dict((a, pref_list) for a, pref_list in pref_listsA)
    E.update(dict((b, pref_list) for b, pref_list in pref_listsB))
    return BipartiteGraph(A, B, E, capacities)


# TODO: verify if correct
def to_networkx_graph(G):
    """
    returns G in networkx format
    :param G: bipartite graph
    :return: G in networkx graph format
    """
    G_ = nx.Graph()
    # add the vertices
    G_.add_nodes_from(G.A, bipartite=0)  # partition A
    G_.add_nodes_from(G.B, bipartite=1)  # partition B
    # add edges
    for a in G.A:
        for b in G.E[a]:
            G_.add_edge(a, b)
    return G_


def copy_graph(G):
    """
    create the copy of the graph G
    for use in functions which mutate G
    :param G: bipartite graph
    :return: new bipartite graph, a copy of G
    """
    import copy
    return BipartiteGraph(G.A.copy(), G.B.copy(), copy.deepcopy(G.E), G.capacities.copy())


def lower_quota(u, G):
    return G.capacities[u][0]


def upper_quota(u, G):
    return G.capacities[u][1]


def graph_to_UTF8_string(G):
    """
    returns the string representation of the graph in UTF-8 format
    :param G: bipartite graph
    :return: string representation of G
    """
    def to_str(u, pref_list, fn=lambda x: x):
        """
        string representation of u along with its preference list
        :param u: vertex name/id
        :param pref_list: a list of vertices ordered
                         according to their rank
        :param fn: function to extract the printable attribute in the partitions
        :return: string representation of u's preference list
        """
        return "{} : {} ;".format(u, ', '.join(map(fn, pref_list)))

    l = list()
    # vertices in partition A
    l.append('@PartitionA\n')
    l.append(', '.join(G.A))
    l.append(' ;\n@End\n')

    # vertices in partition B
    l.append('\n@PartitionB\n')
    l.append(', '.join(map(lambda b: '{} {}'.format(b, G.capacities[b]),
                            G.B)))
    l.append(' ;\n@End\n')

    # preference lists for vertices in partition A
    l.append('\n@PreferenceListsA\n')
    for a in G.A:
        l.append('{}\n'.format(to_str(a, G.E[a])))
    l.append('@End\n')

    # preference lists for vertices in partition B
    l.append('\n@PreferenceListsB\n')
    for b in G.B:
        l.append('{}\n'.format(to_str(b, G.E[b])))
    l.append('@End\n')
    return ''.join(l)


def graph_to_byte_string(G):
    """
    returns the string representation of the graph in byte format
    :param G: bipartite graph
    :return: string representation of G
    """
    return bytes(graph_to_UTF8_string(G), 'UTF-8')


def update_pref_lists(a, b, A, B):
    """
    from b's preference list remove any vertex ranked below a
    also remove b from the preference list of the vertices removed
    :param a: vertex
    :param b: vertex
    :param A: dict containing the pref list for a
    :param B: dict containing the pref list for b
    :return: None
    """
    pref_list = B[b] # b's pref list
    index = pref_list.index(a)
    # remove b from the preference list
    for i in range(index+1, len(pref_list)):
        A[pref_list[i]].remove(b)
    B[b] = pref_list[:index+1]


# TODO: debug this
def to_graphviz(G, M, out):
    """
    print a graphviz representation of M
    with edges not in M labeled with the
    votes of the endpoints
    :param G: bipartite graph
    :param M: matching on G
    :param out: output stream
    :return: None
    """
    def vote(u, v, M_u, pref_list):
        """
        get vote for the edge (u, v) from u's perspective
        :param u: vertex in G
        :param v: vertex in G
        :param M_u: matched partner of u, None if u is unmatched
        :param pref_list: preference list for u
        :return:
        """

        if M_u is None: return +1 # u prefers to be matched
        return +1 if pref_list.index(v) < pref_list.index(M_u) else -1

    # return the edge labeling
    def edge_label(a, b):
        M_a, M_b = M.get(a), M.get(b)
        if M_a == b and M_b == a: # this edge is in the matching
            return '[color=red, penwidth=3.0]'
        else:
            vote_a = vote(a, b, M_a, G.E[a])
            vote_b = vote(b, a, M_b, G.E[b])
            return '[label="({}, {})"]'.format(vote_a, vote_b)

    # print G with edges in E \ M labeled
    print('graph {', file=out)
    for a in G.A:
        for b in G.E[a]:
            print('  {} -- {} {} ;'.format(a, b, edge_label(a, b)), file=out)
    print('}', file=out)


def compare_matchings(G, M1, M2):
    """
    generator to return the votes of the vertices in G
    w.r.t two matchings M1 and M2
    vote is +1 if u prefers M1 to M2,
    -1 if u prefers M2 to M1,
    0 if indifferent
    :param G: bipartite graph
    :param M1: matching on G
    :param M2: matching on G
    :return: generates tuples (a, vote_a)
    """
    # does u prefer M1 over M2
    # +1 if yes, -1 if no, 0 if indifferent
    def prefers_to(u, pref_list):
        # u is matched in M1 and unmatched in M2
        if u in M1 and u not in M2: return +1
        # u is unmatched in M1 and matched in M2
        if u not in M1 and u in M2: return -1
        # u is matched in both
        if u in M1 and u in M2:
            indexa, indexb = pref_list.index(M1[u]), pref_list.index(M2[u])
            if indexa == indexb: return 0  # indifferent
            return +1 if indexa < indexb else -1  # prefers M1(u) to M2(u)
        return 0  # indifferent, unmatched in both

    # yield the votes
    for a in G.A: yield a, prefers_to(a, G.E[a])
    for b in G.B: yield b, prefers_to(b, G.E[b])


def tabulate_matching_comparison(G, M1, M2):
    """
    tabulate the votes in a pretty format
    :param G: bipartite graph
    :param M1: matching on G
    :param M2: matching on G
    :return: string containing tabular representation of votes
    """
    from tabulate import tabulate

    def vote_repr(u, vote):
        # \u2714 is the tick sign
        if vote == 0: return u, '-', '-'
        return (u, '\u2714', '') if vote == +1 else (u, '', '\u2714')
    data = map(lambda x: vote_repr(x[0], x[1]), compare_matchings(G, M1, M2))
    return tabulate(data,
                    headers=['vertex', 'M1', 'M2'],
                    tablefmt="fancy_grid")


def to_easy_format(G, M):
    """
    returns a string with the vertices and their matched partners
    in [(u, M(u)), ...] format for all u in G.A U G.B
    :param G:
    :param M:
    :return:
    """
    return ', '.join('({}, {})'.format(a, M[a]) for a in G.A if a in M)


def main():
    import sys
    import graph_parser
    import matching_algos
    if len(sys.argv) < 2:
        print('usage: {} <graph file>'.format(sys.argv[0]))
    else:
        G = graph_parser.read_graph(sys.argv[1])
        M1 = matching_algos.stable_matching_man_woman(copy_graph(G))
        M2 = matching_algos.popular_matching_man_woman(copy_graph(G))
        print(to_easy_format(G, M1), to_easy_format(G, M2), sep='\n')
        # print(M1, M2, tabulate_matching_comparison(G, M1, M2), sep='\n', file=sys.stdout)
        # graph.to_graphviz(G, M1, sys.stdout)

if __name__ == '__main__':
    main()
