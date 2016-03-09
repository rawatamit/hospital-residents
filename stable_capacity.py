import graph
import graph_parser
import heapq
import copy
import collections
import functools
import itertools

# TODO: clean this up

# returns a two element tuple
# which tells which matching the
# resident prefers
def resident_vote(r, M1, M2):
    M1_r, M2_r = M1.get(r, None), M2.get(r, None)
    if M1_r == M2_r: return 0, 0  # indifferent
    if M1_r is not None: return 1, 0  # r prefers M1
    if M2_r is not None: return 0, 1  # r prefers M2


def hospital_vote(h, M1, M2, preflist):
    # order residents according to h's preference list
    def order_residents(h, M_h, xor):
        return sorted(filter(lambda x: x in xor, M_h),
                      key=lambda x: preflist.index(x))

    def vote(u, v):
        if u is None: return 1, 0
        if v is None: return 0, 1
        return (1, 0) if preflist.index(u) < preflist.index(v) else (0, 1)

    def vote_sum(x, acc):
        u_vote, v_vote = vote(x[0], x[1])
        return u_vote + acc[0], v_vote + acc[1]

    M1_h, M2_h = M1.get(h, None), M2.get(h, None)
    if M1_h == M2_h: return 0, 0  # indifferent
    if M1_h is None: return 0, len(M2_h)  # h is not matched to any resident in M1
    if M2_h is None: return len(M1_h), 0  # h is not matched to any resident in M2
    xor = M1_h ^ M2_h  # we only care about the residents that differ
    M1_ordered = order_residents(h, M1_h, xor)
    M2_ordered = order_residents(h, M2_h, xor)

    # count the votes for M1 and M2
    M1_votes, M2_votes = 0, 0
    for u, v in itertools.zip_longest(M1_ordered, M2_ordered):
        x, y = vote(u, v)
        M1_votes += x
        M2_votes += y
    return M1_votes, M2_votes


def compare_matchings(M1, M2, G):
    resident_votes = map(lambda r: resident_vote(r, M1, M2), G.A)
    hospital_votes = map(lambda h: hospital_vote(h, M1, M2, G.E[h]), G.B)
    sigma_r = functools.reduce(lambda x, y: (x[0] + y[0], x[1] + y[1]), resident_votes, (0, 0))
    sigma_h = functools.reduce(lambda x, y: (x[0] + y[0], x[1] + y[1]), hospital_votes, (0, 0))
    return sigma_h[0] + sigma_r[0], sigma_h[1] + sigma_r[1]


def main():
    import sys
    if len(sys.argv) < 2:
        print('usage: {} <graph file>'.format(sys.argv[0]))
    else:
        G = graph_parser.read_graph(sys.argv[1])
        #print(augment_graph(G), sep='\n') #stable_capacity(G))

if __name__ == '__main__':
    main()
