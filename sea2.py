import os
import sea
import graph
import graph_parser
import matching_algos
import matching_utils


def is_graph_file(entry):
    return (entry.is_file()
            and not entry.name.startswith(sea.MAXIMAL_ENVYFREE)
            and not entry.name.startswith('stats'))


def corr_matching_and_stats(entry, matching):
    dirpath = os.path.dirname(entry.path)
    return (os.path.join(dirpath, '{}{}'.format(matching, entry.name)),
            os.path.join(dirpath, 'stats_{}'.format(entry.name)) )


def blocking_residents(G, bpairs):
    bres = set()
    for a, b in bpairs:
        if a in G.A: bres.add(a)
        if b in G.A: bres.add(b)
    return bres


def rank_1_residents(G, M):
    return [a for a in G.A if a in M and G.E[a].index(M[a]) == 0]


def print_matching_stats(G, M, filepath):
    size = matching_utils.matching_size(G, M)
    bpairs = matching_utils.unstable_pairs(G, M)
    bres = blocking_residents(G, bpairs)
    rank1 = rank_1_residents(G, M)
    M_s = matching_algos.stable_matching_hospital_residents(graph.copy_graph(G))

    with open(filepath, mode='w', encoding='utf-8') as out:
        print('size: {}'.format(size), file=out)
        print('# blocking pair: {}'.format(len(bpairs)), file=out)
        print('# blocking residents: {}'.format(len(bres)), file=out)
        print('# residents matched to rank-1 partners: {}'.format(len(rank1)), file=out)
        print('total deficiency: {}'.format(sea.total_deficiency(G, M_s)), file=out)


def is_matched_edge(M, u, v):
    return u in M and v in M and v in M[u]


def unmatched_edges(G, M):
    uedges = {}

    for a in G.A:
        for b in G.E[a]:
            if a not in M and not is_matched_edge(M, a, b):
                uedges[a] = b
    
    return uedges


# does r_ has justified envy towards r
def has_envy(G, M, r_, r, h):
    # r_ is unmatched or prefers h over M[r_]
    if ((r_ not in M or G.E[r_].index(h) < G.E[r_].index(M[r_])) and
        # h prefers r_ over r
        G.E[h].index(r_) < G.E[h].index(r)):
            return True
    return False


def generate_stats(dirpath):
    for entry in os.scandir(dirpath):
        if entry.is_file():
            if is_graph_file(entry):
                mpath, statpath = corr_matching_and_stats(entry, sea.MAXIMAL_ENVYFREE)
                if os.path.isfile(mpath):
                    M = sea.read_matching(mpath)
                    if len(M) != 0:
                        G = graph_parser.read_graph(entry.path)
                        print_matching_stats(G, M, statpath)
        elif entry.is_dir():
            generate_stats(entry.path)


if __name__ == '__main__':
    DIRPATH = '/mnt/f55c6248-0895-4d46-8d0e-1db681847773/meghana/sea/popular/HRLQ'
    generate_stats(DIRPATH)
