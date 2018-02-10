import os
import sea
import graph
import graph_parser
import matching_utils


def is_graph_file(entry):
    return entry.is_file() and not entry.name.startswith('E')


def corr_matching_and_stats(entry):
    dirpath = os.path.dirname(entry.path)
    return (os.path.join(dirpath, 'E_{}'.format(entry.name)),
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

    with open(filepath, mode='w', encoding='utf-8') as out:
        print('size: {}'.format(size), file=out)
        print('# blocking pair: {}'.format(len(bpairs)), file=out)
        print('# blocking residents: {}'.format(len(bres)), file=out)
        print('# residents matched to rank-1 partners: {}'.format(len(rank1)), file=out)


def recurse_dir(dirpath):
    for entry in os.scandir(dirpath):
        if entry.is_file():
            if is_graph_file(entry):
                mpath, statpath = corr_matching_and_stats(entry)
                if os.path.isfile(mpath):
                    M = sea.read_matching(mpath)
                    G = graph_parser.read_graph(entry.path)
                    print_matching_stats(G, M, statpath)
        elif entry.is_dir():
            recurse_dir(entry.path)


def is_matched_edge(M, u, v):
    return u in M and v in M and v in M[u]


def unmatched_edges(G, M):
    uedges = {}

    for a in G.A:
        for b in G.E[a]:
            if not is_matched_edge(M, a, b):
                uedges[a] = b
                # uedges[b] = a
    
    return uedges


# does r_ has justified envy towards r
def has_envy(G, M, r_, r):
    h = M[r]

    # r_ provides preference for h
    if (G.E[r_].count(h) != 0 and
        # r_ is unmatched or prefers h over M[r_]
        (r_ not in M or G.E[r_].index(h) < G.E[r_].index(M[r_])) and
        # h prefers r_ over r
        G.E[h].index(r_) < G.E[h].index(r)):
            return True
    return False


def envy_free_matching(G, M):
    uedges = unmatched_edges(G, M)

    # for each unmatched edge
    for r, h in uedges.items():
        # match r and h only if h can accomodate one more resident
        # this could be two cases, either h is matched in M, then |M(h)| < q+(h)
        # or h is unmatched in M
        if h not in M or len(M[h]) < graph.upper_quota(G, h):
            # save old M[r] and M[h]
            M_r = M[r] if r in M else None
            M_h = M[h] if h in M else None

            # add edge to matching
            M[r] = h

            if h in M: M[h].add(r)
            else: M[h] = {r}
            
            # every non matched resident to h in h's pref list
            for r_ in G.E[h]:
                if r_ not in M:
                    # this matching is not envy free
                    # remove the edge we just added
                    if has_envy(G, M, r_, r):
                        if M_r is None: del M[r]
                        else: M[r] = M_r
                
                        if M_h is None: del M[h]
                        else: M[h] = M_h

                        break # justified envy, no need to check further
    
    return M


def is_envy_maximal(dirpath):
    for entry in os.scandir(dirpath):
        if entry.is_file():
            if is_graph_file(entry):
                mpath, statpath = corr_matching_and_stats(entry)
                if os.path.isfile(mpath):
                    M = sea.read_matching(mpath)
                    G = graph_parser.read_graph(entry.path)
                    M_ = envy_free_matching(G, M)
                    if M != M_: print('not same for {}'.format(entry.path))
        elif entry.is_dir():
            is_envy_maximal(entry.path)


def gen_matching():
    import sys
    gfile, mfile = sys.argv[1], sys.argv[2]
    M = sea.read_matching(mfile)
    M_ = envy_free_matching(graph_parser.read_graph(gfile), M)
    print(M==M_)


if __name__ == '__main__':
    DIRPATH = '/home/student/Desktop/sea/popular/HRLQ'
    is_envy_maximal(DIRPATH)
