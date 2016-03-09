import ply.yacc as yacc
from graph_lexer import tokens  # get the token map from the lexer
import sys
import graph


# TODO: fix this, so that we can have nodes and edges in any order
# the grammar is not clean
def p_graph(p):
    """graph : nodes nodes edges edges"""
    p[0] = p[1], p[2], p[3], p[4]


def p_partition_A(p):
    """nodes : PARTITION_A pvertex_list ';' END"""
    p[0] = p[2]


def p_partition_B(p):
    """nodes : PARTITION_B pvertex_list ';' END"""
    p[0] = p[2]


# the vertex list for the partitions
def p_pvertex_list(p):
    """pvertex_list : pvertex_list ',' pvertex"""
    p[0] = p[1] + [p[3]]


def p_pvertex_list_terminating(p):
    """pvertex_list : pvertex"""
    p[0] = [p[1]]


# rules for a vertex declaration in vertex list
def p_pvertex(p):
    """pvertex : ID"""
    p[0] = (p[1], 1)


def p_pvertex_capacity(p):
    """pvertex : ID '(' INT ')'"""
    p[0] = (p[1], p[3])


def p_vertex_list(p):
    """vertex_list : vertex_list ',' ID"""
    p[0] = p[1] + [p[3]]


def p_vertex_list_terminating(p):
    """vertex_list : ID"""
    p[0] = [p[1]]


def p_preference_lists_A(p):
    """edges : PREFERENCE_LISTS_A preference_lists END"""
    p[0] = p[2]


def p_preference_lists_B(p):
    """edges : PREFERENCE_LISTS_B preference_lists END"""
    p[0] = p[2]


def p_preference_lists(p):
    """preference_lists : preference_lists pref_list"""
    p[0] = p[1] + [p[2]]


def p_preference_lists_terminating(p):
    """preference_lists : pref_list"""
    p[0] = [p[1]]


def p_pref_list(p):
    """pref_list : ID ':' vertex_list ';'"""
    p[0] = p[1], p[3]


# error rule for syntax errors
def p_error(p):
    if p:
        print("error: token {} at line {}".format(p.type, p.lineno), file=sys.stderr)
        # discard the token and tell the parser it's okay.
        parser.errok()
    else:
        print("error: EOF before parsing could finish.", file=sys.stderr)


# build the parser
parser = yacc.yacc(debug=0)


def read_graph(file_path):
    with open(file_path, encoding='utf-8', mode='r') as fin:
        A, B, pref_listA, pref_listB = parser.parse(fin.read())
        # map of the capacities
        capacities = dict(A)
        capacities.update(dict(B))
        A = set(id for id, _ in A)
        B = set(id for id, _ in B)
        pref_listA = [(a, list(b)) for a, b in pref_listA]
        pref_listB = [(a, list(b)) for a, b in pref_listB]
        return graph.make_graph(A, B, pref_listA, pref_listB, capacities)


def main():
    if len(sys.argv) < 2:
        print('usage: {} <graph file path>'.format(sys.argv[0]), file=sys.stderr)
    else:
        file_path = sys.argv[1]
        print(read_graph(file_path))

if __name__ == '__main__':
    main()
