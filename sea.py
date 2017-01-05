import sys
import csv
import graph
import graph_parser
import matching_utils
import collections
from tabulate import tabulate
from pylatex.utils import italic
from pylatex import Document, Section, Subsection, Tabular, MultiColumn, MultiRow


# matching descriptions
STABLE = 'stable'
POPULAR = 'popular'
DESC = (STABLE, POPULAR)


def count_if(G, M1, M2, f):
    """
    count men on choice between M1 and M2
    :param G: bipartite graph
    :param M1: first matching
    :param M2: second matching
    :param f: predicate function
    """
    count = 0
    for u in G.A:
        M1_u, M2_u = M1.get(u), M2.get(u)
        count += 1 if f(G, u, M1_u, M2_u) else 0
    return count


def better(G, u, M1_u, M2_u):
    # M1_u is not better than M2_u
    if M1_u is None and M2_u is None: return False
    if M1_u is None: return False
    # M1_u is better than M2_u
    if M2_u is None: return True
    return G.E[u].index(M1_u) < G.E[u].index(M2_u)


def equal(G, u, M1_u, M2_u):
    # M1_u is equal to M2_u
    if M1_u is None and M2_u is None: return True
    # M1_u is not equal to M2_u
    if M1_u is None: return False
    if M2_u is None: return False
    return G.E[u].index(M1_u) == G.E[u].index(M2_u)


def worse(G, u, M1_u, M2_u):
    # M1_u is not worse than M2_u
    if M1_u is None and M2_u is None: return False
    if M2_u is None: return True
    # M1_u is worse than M2_u
    if M1_u is None: return True
    return G.E[u].index(M1_u) > G.E[u].index(M2_u)


def nmatched_pairs(G, M):
    """
    number of matched pairs in M
    :param M: feasible matching in G
    :return: # of matched pairs in M
    """
    return sum(1 for a in G.A if a in M)


def sum_ranks(sig, ranks):
    """
    number of vertices matched to one of the given ranks in the signature
    :param sig: matching signature
    """
    return sum([sig[rank] for rank in ranks if rank in sig])


def signature(G, M):
    """
    signature of the matching
    :param G: bipartite graph
    :param M: a matching in G
    """
    sig = collections.defaultdict(int)
    for a in G.A:
        if a in M:
            index = G.E[a].index(M[a]) + 1
            sig[index] += 1
    return sig


def generate_tex(G, matchings):
    """
    print statistics as a tex file
    :param G: graph
    :param matchings: information about the matchings
    """
    M_stable = matchings[STABLE]
    M_popular = matchings[POPULAR]

    # create a tex file with the statistics
    doc = Document('table')
    with doc.create(Section('matching statistics')):
        with doc.create(Tabular('|c|c|c|c|c|c|c|c|')) as table:
            table.add_hline()
            table.add_row(('description', 'size', '# unstable pairs',
                           'A rank-1', 'A rank-upto-3',
                           'A better', 'A equal', 'A worse'))
            for desc in DESC:
                M = matchings[desc]
                sig = signature(G, M)
                M1 = M_stable if DESC == POPULAR else M_popular
                table.add_hline()
                table.add_row((desc, italic(nmatched_pairs(G, M)),
                              len(matching_utils.unstable_pairs(G, M)),
                              sum_ranks(sig, (1,)), sum_ranks(sig, (1, 2, 3)),
                              count_if(G, M, M1, better), count_if(G, M, M1, equal),
                              count_if(G, M, M1, worse)))
            table.add_hline()

    doc.generate_pdf('stats', clean_tex='False')
    doc.generate_tex()


def read_matching(G, file_name):
    with open(file_name, newline='', encoding='utf-8') as rdr:
        M = {}
        for row in csv.reader(rdr, delimiter=','):
            # add M(r) = h
            M[row[0]] = row[1]

            # add M(h) = {r_1, ..., r_k}
            if row[1] in M:
                M[row[1]].add(row[0])
            else:
                M[row[1]] = {row[0]}
        return M


def statistics_to_latex(G_file, stable_file, pop_file):
    G = graph_parser.read_graph(G_file)
    matchings = {STABLE: read_matching(G, stable_file),
                 POPULAR: read_matching(G, pop_file)}
    generate_tex(G, matchings)


def main():
    if len(sys.argv) < 4:
        print('usage: {} <graph-file> <stable-file> <popular-file>'.format(sys.argv[0]))
    else:
        G_file = sys.argv[1]
        stable_file, pop_file = sys.argv[2], sys.argv[3]
        statistics_to_latex(G_file, stable_file, pop_file)

if __name__ == '__main__':
    main()
