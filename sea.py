import os
import sys
import csv
import argparse
import graph
import graph_parser
import matching_algos
import matching_utils
import collections
from tabulate import tabulate
from pylatex.utils import italic
from pylatex import Document, Section, Subsection, Tabular, MultiColumn, MultiRow


# matching descriptions
STABLE = 'S'
MAX_CARD_POPULAR = 'P'
POP_AMONG_MAX_CARD = 'M'
HRLQ_HHEURISTIC = 'H'
HRLQ_RHEURISTIC = 'R'
DESC = (STABLE, MAX_CARD_POPULAR, POP_AMONG_MAX_CARD)
OTHER = {STABLE: [MAX_CARD_POPULAR, POP_AMONG_MAX_CARD],
         MAX_CARD_POPULAR: [STABLE, POP_AMONG_MAX_CARD],
         POP_AMONG_MAX_CARD: [STABLE, MAX_CARD_POPULAR]}


def count_if(G, M1, M2, f, A=True):
    """
    count men on choice between M1 and M2
    :param G: bipartite graph
    :param M1: first matching
    :param M2: second matching
    :param f: predicate function
    :param A: True if processing partition A, False otherwise
    """
    count = 0
    partition = G.A if A else G.B
    for u in partition:
        M1_u, M2_u = M1.get(u), M2.get(u)
        r= f(G, u, M1_u, M2_u)
        count += 1 if f(G, u, M1_u, M2_u) else 0
    return count


def better(G, u, M1_u, M2_u):
    """
    is M1_u better than M2_u
    """
    # M1_u is not better than M2_u
    if M1_u is None and M2_u is None: return False
    if M1_u is None: return False
    # M1_u is better than M2_u
    if M2_u is None: return True
    return G.E[u].index(M1_u) < G.E[u].index(M2_u)


def equal(G, u, M1_u, M2_u):
    """
    is M1_u equal to M2_u
    """
    # M1_u is equal to M2_u
    if M1_u is None and M2_u is None: return True
    # M1_u is not equal to M2_u
    if M1_u is None: return False
    if M2_u is None: return False
    return G.E[u].index(M1_u) == G.E[u].index(M2_u)


def worse(G, u, M1_u, M2_u):
    """
    is M1_u worse than M2_u
    """
    # M1_u is not worse than M2_u
    if M1_u is None and M2_u is None: return False
    if M2_u is None: return False
    # M1_u is worse than M2_u
    if M1_u is None: return True
    return G.E[u].index(M1_u) > G.E[u].index(M2_u)


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


def matched_in_stable(G, M_s, M_p):
    """
    number of pairs that are supposed to be
    present in a stable matching in G
    :param G: bipartite graph
    """
    count = 0
    count_p = 0
    for a in G.A:
        b = G.E[a][0]
        if a in G.E[b][:graph.upper_quota(G, b)]:
            count += 1
            if M_s[a] != b:
                raise Exception
            if M_p[a] == b:
                count_p += 1
    return count, count_p


def total_deficiency(G, M):
    """
    return total deficiency of the lower quota hospitals
    :param G: graph
    :param M: matching in G
    """
    sum_def = 0
    for h in G.B:
        lq = graph.lower_quota(G, h)
        if lq > 0:
            nmatched = len(matching_utils.partners_iterable(G, M, h))
            deficiency = lq - nmatched
            sum_def += deficiency if deficiency > 0 else 0
    return sum_def


def blocking_residents(bp):
    """
    returns the set of blocking residents given the list
    of blocking pairs
    :param bp: list of blocking pairs
    """
    return set(a for a, _ in bp)


def stats_for_partition(G, matchings, doc, A=True):
    """
    print statistics for the partition specified
    :param G: graph
    :param matchings: information about the matchings
    :param doc: document to emit the stats
    :param A: True if emitting stats for partition A, False for B
    """
    section_name = 'A' if A else 'B'
    with doc.create(Subsection('{} statistics'.format(section_name))):
        with doc.create(Tabular('|c|c|c|c|')) as table:
            table.add_hline()
            table.add_row(('vs', 'rank-1', 'rank-upto-3', 'better'))
            for desc in DESC:
                M = matchings[desc]
                sig = signature(G, M)
                for other in OTHER[desc]:
                    M1 = matchings[other]
                    table.add_hline()
                    table.add_row(('{}/{}'.format(desc, other),
                                   sum_ranks(sig, (1,)), sum_ranks(sig, (1, 2, 3)),
                                   count_if(G, M, M1, better)))
            table.add_hline()


def generate_hr_tex(G, matchings, output_dir, stats_filename):
    """
    print statistics for the resident proposing stable,
    max-cardinality popular, and popular amongst max-cardinality
    matchings as a tex file
    :param G: graph
    :param matchings: information about the matchings
    """
    # create a tex file with the statistics
    doc = Document('table')
    # M_s = matching_algos.stable_matching_hospital_residents(graph.copy_graph(G))

    # add details about the graph, |A|, |B|, and # of edges
    n1, n2, m = len(G.A), len(G.B), sum(len(G.E[r]) for r in G.A)
    with doc.create(Subsection('graph details')):
        with doc.create(Tabular('|c|c|')) as table:
            table.add_hline()
            table.add_row('n1', n1)
            table.add_hline()
            table.add_row('n2', n1)
            table.add_hline()
            table.add_row('m', m)
        table.add_hline()

    with doc.create(Subsection('general statistics')):
        with doc.create(Tabular('|c|c|c|c|')) as table:
            table.add_hline()
            table.add_row(('description', 'size', 'bp', 'bp ratio'))
            for desc in matchings:
                M = matchings[desc]
                sig = signature(G, M)
                msize = matching_utils.matching_size(G, M)
                bp = matching_utils.unstable_pairs(G, M)
                table.add_hline()
                table.add_row((desc, msize, len(bp), len(bp)/(m - msize)))
            table.add_hline()

    # statistics w.r.t. set A
    stats_for_partition(G, matchings, doc)

    # statistics w.r.t. set B
    # stats_for_partition(G, matchings, doc, False)

    stats_abs_path = os.path.join(output_dir, stats_filename)
    doc.generate_pdf(filepath=stats_abs_path, clean_tex='False')
    doc.generate_tex(filepath=stats_abs_path)


def generate_heuristic_tex(G, matchings, output_dir, stats_filename):
    """
    print statistics for the hospital proposing heuristic as a tex file
    :param G: graph
    :param matchings: information about the matchings
    """
    # create a tex file with the statistics
    doc = Document('table')

    # add details about the graph, |A|, |B|, and # of edges
    n1, n2, m = len(G.A), len(G.B), sum(len(G.E[r]) for r in G.A)
    with doc.create(Subsection('graph details')):
        with doc.create(Tabular('|c|c|')) as table:
            table.add_hline()
            table.add_row('n1', n1)
            table.add_hline()
            table.add_row('n2', n1)
            table.add_hline()
            table.add_row('m', m)
        table.add_hline()

    M_s = matching_algos.stable_matching_hospital_residents(graph.copy_graph(G))
    with doc.create(Subsection('Size statistics')):
        with doc.create(Tabular('|c|c|c|c|c|c|c|')) as table:
            table.add_hline()
            table.add_row(('description', 'size', 'bp', 'bp ratio', 'block-R',
                           'rank-1', 'deficiency'))
            for desc in matchings:
                M = matchings[desc]
                sig = signature(G, M)
                bp = matching_utils.unstable_pairs(G, M)
                msize = matching_utils.matching_size(G, M)
                table.add_hline()
                table.add_row((desc, msize, len(bp), len(bp)/(m - msize),
                               len(blocking_residents(bp)),
                               sum_ranks(sig, (1,)), #sum_ranks(sig, (1, 2, 3)),
                               total_deficiency(G, M_s)))
            table.add_hline()

    stats_abs_path = os.path.join(output_dir, stats_filename)
    doc.generate_pdf(filepath=stats_abs_path, clean_tex='False')
    doc.generate_tex(filepath=stats_abs_path)


def read_matching(file_name):
    with open(file_name, newline='', encoding='utf-8') as rdr:
        M = {}
        for row in csv.reader(rdr, delimiter=','):
            # M(r) = h
            M[row[0]] = row[1]

            # M(h) = {r_1, ..., r_k}
            if row[1] in M:
                M[row[1]].add(row[0])
            else:
                M[row[1]] = {row[0]}
        return M


def main():
    parser = argparse.ArgumentParser(description='''Generate statistics in latex
                                format given a bipartite graph and matchings''')
    parser.add_argument('-G', dest='G', help='Bipartite graph', required=True, metavar='')
    parser.add_argument('-S', dest='S', help='Stable matching in the graph', metavar='')
    parser.add_argument('-P', dest='P', help='Max-cardinality popular matching in the graph', metavar='')
    parser.add_argument('-M', dest='M', help='Popular among max-cardinality matchings in the graph', metavar='')
    parser.add_argument('-H', dest='H', help='Hospital proposing HRLQ heuristic in the graph', metavar='')
    parser.add_argument('-R', dest='R', help='Resident proposing HRLQ heuristic in the graph', metavar='')
    parser.add_argument('-O', dest='O', help='Directory where the statistics should be stored', metavar='')
    args = parser.parse_args()

    G, matchings = graph_parser.read_graph(args.G), {}
    for mdesc, mfile in ((STABLE, args.S), (MAX_CARD_POPULAR, args.P),
                         (POP_AMONG_MAX_CARD, args.M), (HRLQ_HHEURISTIC, args.H),
                         (HRLQ_RHEURISTIC, args.R)):
        if mfile is not None:
            M = read_matching(mfile)
            matchings[mdesc] = M
            # if not matching_utils.is_feasible(G, M):
                # raise Exception('{} matching is not feasible for the graph'.format(mdesc))
    # print(args.H, matchings)
    if args.H: # generate heuristic tex file
        generate_heuristic_tex(G, matchings, args.O, os.path.basename(args.G))
    else: # generate tex for M_s, M_p, and M_m
        generate_hr_tex(G, matchings, args.O, os.path.basename(args.G))


if __name__ == '__main__':
    main()
