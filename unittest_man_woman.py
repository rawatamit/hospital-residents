import unittest
import graph
import matching_algos


def make_graph(plistA, plistB):
    A = set(x[0] for x in plistA)
    B = set(x[0] for x in plistB)
    capacities = dict((a, 1) for a in A)
    capacities.update(dict((b, 1) for b in B))
    return graph.make_graph(A, B, plistA, plistB, capacities)


def matched_pairs_to_dict(M):
    D = dict((a, b) for a, b in M)
    D.update(dict((b, a) for a, b in M))
    return D


"""
def is_stable(G, M):
    # does a prefer b over c
    def prefers(a, b, c):
        if c is None: return True  # true if c is None
        if b is None: return False  # false if b is None
        # check their relative ordering in a's pref list
        return G.E[a].index(b) < G.E[a].index(c)

    for a in G.A:  # for each vertex in a
        index, partner, pref_list = 0, M.get(a), G.E[a]
        # while a prefers a woman to its matched partner in its pref list
        while index < len(pref_list) and prefers(a, pref_list[index], partner):
            b = pref_list[index]
            # if b also prefers a to its matched partner
            if prefers(b, a, M.get(b)):
                return False  # this matching is unstable
            index += 1
    return True
"""


def is_stable(G, M):
    upairs = matching_algos.unstable_pairs(G, M)
    return len(upairs) == 0


class TestGaleShapley(unittest.TestCase):
    def test_g1(self):
        """
        I = {a1 : b1 ;
             b1 : a1 ;}
        """
        G = make_graph(
                [('a1', ['b1'])],
                [('b1', ['a1'])])
        self.assertTrue(
                is_stable(G, matching_algos.stable_matching_man_woman(graph.copy_graph(G))))

    def test_g2(self):
        """
        I = {A : Y,X,Z ; B : Z,Y,X ; C : X,Z,Y ;
             X : B,A,C ; Y : C,B,A ; Z : A,C,B ; }
        """
        G = make_graph(
                [('A', ['Y', 'X', 'Z']), ('B', ['Z', 'Y', 'X']), ('C', ['X', 'Z', 'Y'])],
                [('X', ['B', 'A', 'C']), ('Y', ['C', 'B', 'A']), ('Z', ['A', 'C', 'B'])])
        self.assertTrue(
                is_stable(G, matching_algos.stable_matching_man_woman(graph.copy_graph(G))))

    def test_g3(self):
        """
        I = {A : Y,X,Z ; B : X,Y,Z ; C : X,Y,Z ;
             X : A,B,C ; Y : B,A,C ; Z : A,B,C ; }
        """
        G = make_graph(
                [('A', ['Y', 'X', 'Z']), ('B', ['X', 'Y', 'Z']), ('C', ['X', 'Y', 'Z'])],
                [('X', ['A', 'B', 'C']), ('Y', ['B', 'A', 'C']), ('Z', ['A', 'B', 'C'])])
        self.assertTrue(
                is_stable(G, matching_algos.stable_matching_man_woman(graph.copy_graph(G))))

    def test_g4(self):
        """
        I = {m1 : w2,w4,w1,w3 ; m2 : w3,w1,w4,w2 ; m3 : w2,w3,w1,w4 ; m4 : w4,w1,w3,w2 ;
             w1 : m2,m1,m4,m3 ; w2 : m4,m3,m1,m2 ; w3 : m1,m4,m3,m2 ; w4 : m2,m1,m4,m3 ;}
        """
        G = make_graph(
                [('m1', ['w2', 'w4', 'w1', 'w3']), ('m2', ['w3', 'w1', 'w4', 'w2']),
                 ('m3', ['w2', 'w3', 'w1', 'w4']), ('m4', ['w4', 'w1', 'w3', 'w2'])],
                [('w1', ['m2', 'm1', 'm4', 'm3']), ('w2', ['m4', 'm3', 'm1', 'm2']),
                 ('w3', ['m1', 'm4', 'm3', 'm2']), ('w4', ['m2', 'm1', 'm4', 'm3'])])
        self.assertTrue(
                is_stable(G, matching_algos.stable_matching_man_woman(graph.copy_graph(G))))


class TestKavitaAlgorithm1(unittest.TestCase):
    def test_g1(self):
        """
        I = {a1 : b1 ;
             b1 : a1 ;}
        M = {(a1, b1)}
        """
        G = make_graph(
                [('a1', ['b1'])],
                [('b1', ['a1'])])
        M = matched_pairs_to_dict([('a1', 'b1')])
        M_kavita = matching_algos.popular_matching_man_woman(graph.copy_graph(G))
        self.assertEqual(M, M_kavita)
    
    def test_g2(self):
        """
        I = {a1 : b1, b2 ; a2 : b1 ;
             b1 : a1, a2 ; b2 : a1 ; }
        M = {(a1, b2), (a2, b1)}
        """
        G = make_graph(
                [('a1', ['b1', 'b2']), ('a2', ['b1'])],
                [('b1', ['a1', 'a2']), ('b2', ['a1'])])
        M = matched_pairs_to_dict([('a1', 'b2'), ('a2', 'b1')])
        M_kavita = matching_algos.popular_matching_man_woman(graph.copy_graph(G))
        self.assertEqual(M, M_kavita)

if __name__ == '__main__':
    unittest.main()
