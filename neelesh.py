import graph
import graph_parser
import stable_capacity
import csv
import collections
import random
import tempfile
from tabulate import tabulate

Student = collections.namedtuple('Student', ['rollno'])
Elective = collections.namedtuple('Elective', ['id'])


def to_str(id, pref_list, fn=lambda x: x):
    """
    returns a printable string representation of
    a vertex along with its preference list
    :param id: vertex name/id
    :param pref_list: a list of vertices ordered
                     according to their position
    :param fn: function to extract the name
    :return: None
    """
    return "{} : {} ;".format(id, ', '.join(map(fn, pref_list)))


def read_course_allotment_graph(file, skip_header, split_index):
    """
    reads the course allotment graph from the given csv_file
    :param file: file having the graph in CSV format
    :param split_index: where to split a pref list
    :return: bipartite graph with the
    """
    # TODO: lot of hard coded values
    students = set()
    E = collections.defaultdict(list)  # dict to store the preference list

    # skip the header if needed
    if skip_header:
        file.readline()

    # read data
    for row in csv.reader(file):
        # FIXME: ugly code
        rollno, preferences = row[split_index-1], row[split_index:]

        # only add non empty preferences
        pref_list = [Elective(pref) for pref in preferences if pref]

        # do not add an isolated vertex, assume roll numbers are unique
        if pref_list:
            student = Student(rollno)
            students.add(student)
            E[student] = pref_list

    electives = set()
    for student in students:
        for elective in E[student]:
            electives.add(elective)
            E[elective].append(student)

    capacities = dict((student, 1) for student in students)
    # TODO: fix this
    # cap = {Elective('HS1100'): 1, Elective('HS1120'): 1, Elective('HS2200'): 13, Elective('HS2320'): 50,
    #       Elective('HS3060'): 4, Elective('HS3420'): 4, Elective('HS4004'): 21, Elective('HS4180'): 11,
    #       Elective('HS4330'): 22, Elective('HS4370'): 37, Elective('HS5612'): 36, Elective('HS6140'): 50}
    cap = {Elective('HS1090'): 60, Elective('HS2130'): 26, Elective('HS2210'): 106, Elective('HS2370'): 53,
           Elective('HS3002'): 250, Elective('HS3005'): 53, Elective('HS3007'): 36, Elective('HS3029'): 23,
           Elective('HS4050'): 53, Elective('HS4350'): 25, Elective('HS4410'): 50, Elective('HS4480'): 45,
           Elective('HS5080'): 44, Elective('HS5920'): 53, Elective('HS5930'): 53, Elective('HS6130'): 53,
           Elective('HS7004'): 41}
    capacities.update(cap)

    # capacities.update({Elective('MA2010'): 80, Elective('MA2020'): 80,
    #                   Elective('MA2030'): 210, Elective('MA2040'): 350})
    #capacities.update(dict((elective, len(students)) for elective in electives))
    return graph.BipartiteGraph(students, electives, E, capacities)


def random_sample(G):
    """
    generates a random sampling, which is then returned
    as a bipartite graph, from the given graph
    the returned preference lists are symmetric
    :param G: bipartite graph
    :return: bipartite graph from a random sample
    """
    E = collections.defaultdict(list)  # to store the new sampled preference list
    for student in G.A:
        pref_list = G.E[student]
        E[student] = pref_list[:]  # store the pref list of student in E
        # for all the hospitals add the students to their preference list
        for elective in pref_list:
            E[elective].append(student)

    # shuffle the preference list for the electives
    for elective in G.B:
        random.shuffle(E[elective])

    return graph.BipartiteGraph(G.A, G.B, E, G.capacities)


def print_course_allotment_graph(G, out):
    """
    prints the graph to the provided output stream
    :param G: bipartite graph
    :param out: output stream
    :return:
    """
    try:
        out.write(bytes('@PartitionA\n', 'UTF-8'))
        out.write(bytes(', '.join(map(lambda student: student.rollno, G.A)), 'UTF-8'))
        out.write(bytes(' ;\n@End\n', 'UTF-8'))

        out.write(bytes('\n@PartitionB\n', 'UTF-8'))
        out.write(bytes(', '.join(map(lambda elective: '{}({})'.format(elective.id, G.capacities[elective]),
                                      G.B)), 'UTF-8'))
        out.write(bytes(' ;\n@End\n', 'UTF-8'))

        out.write(bytes('\n@PreferenceListsA\n', 'UTF-8'))
        for student in G.A:
            out.write(bytes('{}\n'.format(to_str(student.rollno, G.E[student], lambda x: x.id)), 'UTF-8'))
        out.write(bytes('@End\n', 'UTF-8'))

        # pref list for hospitals
        out.write(bytes('\n@PreferenceListsB\n', 'UTF-8'))
        for elective in G.B:
            out.write(bytes('{}\n'.format(to_str(elective.id, G.E[elective], lambda x: x.rollno)), 'UTF-8'))
        out.write(bytes('@End\n', 'UTF-8'))
    finally:
        out.flush()


def print_matching(G, M, filename):
    """
    prints the matching in the following format to the file:
    roll no, max credits, allotment, credits, index in the pref list
    :param G: bipartite graph
    :param M: matching in G
    :param filename: file to write to
    :return: None
    """
    # TODO: hardcoded values for max credits, and credits
    max_credits, course_credits = 10, 10
    with open(filename, mode='w', encoding='utf-8') as out:
        for student in G.A:
            if student in M:  # only if the student has been alloted to a course
                h = M[student]
                print('{},{},{},{},{}'.format(
                                            student, max_credits,
                                            h, course_credits,
                                            G.E[student].index(h) + 1), file=out)


def unstable_pairs(G, M):
    """
    finds the unstable pairs in G w.r.t matching M
    :param G: bipartite graph
    :param M: matching in G
    :return: list of the unstable pairs
    """
    # order residents according to u's preference list
    def order_residents(u):
        return sorted(M[u], key=G.E[u].index)

    # the least preferred resident this vertex is matched to
    def least_preferred_resident(ordered_residents):
        n = len(ordered_residents)
        return ordered_residents[n-1] if ordered_residents else None

    # does a prefer b over c
    def prefers(a, b, c):
        if c is None: return True  # true if c is None
        if b is None: return False  # false if b is None
        # check their relative ordering in a's pref list
        return G.E[a].index(b) < G.E[a].index(c)

    # mapping of hospitals to their least preferred neighbors in M
    least_preferred = dict((u, least_preferred_resident(order_residents(u))) for u in G.B)
    upairs = []  # unstable pairs
    for a in G.A:  # for each vertex in A
        index, partner, pref_list = 0, M.get(a), G.E[a]
        # while a prefers a woman to its matched partner in its pref list
        while index < len(pref_list) and prefers(a, pref_list[index], partner):
            b = pref_list[index]
            # if b also prefers a to its least preferred partner
            if prefers(b, a, least_preferred[b]):
                upairs.append((a, b))  # this pair is unstable
            index += 1
    return upairs


def matching_stats(G, stable_file, popular_file, stats_file):
    """
    prints the matchings and the stats generated
    :param G: bipartite graph
    :param stable_file: file to output the stable matching
    :param popular_file: file to output the popular matching
    :param stats_file: file to output the statistics generated
    :return: None
    """
    def nmatched_pairs(M):
        """
        :param M: valid matching in G
        :return: # of matched pairs in M
        """
        return sum(len(M[h]) for h in G.B if h in M)

    # generate the stable matching
    M_stable = stable_capacity.stable_capacity(graph.copy_graph(G))
    # write it to the file
    print_matching(G, M_stable, stable_file)

    # augment the graph
    G_ = stable_capacity.augment_graph(G)
    # the popular matching
    M_popular = stable_capacity.stable_capacity(G_, format_to_standard=True)
    # write it to the file
    print_matching(G, M_popular, popular_file)

    # print some stats corresponding to the matchings obtained
    with open(stats_file, encoding='utf-8', mode='w') as fout:
        indices_stable = [G.E[a].index(M_stable[a])+1 for a in G.A if a in M_stable]
        indices_popular = [G.E[a].index(M_popular[a])+1 for a in G.A if a in M_popular]

        table = [['matching desc.', 'matching size', '# unstable pairs',
                  'min index', 'max index', 'avg index'],
                 ['stable', nmatched_pairs(M_stable), len(unstable_pairs(G, M_stable)),
                  min(indices_stable), max(indices_stable), sum(indices_stable)/len(indices_stable)],
                 ['popular', nmatched_pairs(M_popular), len(unstable_pairs(G, M_popular)),
                  min(indices_popular), max(indices_popular), sum(indices_popular)/len(indices_popular)],
                 ['max card.', 'NA', 'NA', 'NA', 'NA', 'NA']]
        print(tabulate(table, headers='firstrow', tablefmt='psql'), file=fout)


def collect_stats(csv_file, skip_header, split_index, iterations, dir):
    """
    interface to the matching_stats function
    :param csv_file: graph in CSV format
    :param iterations: # of different random instances to run on
    :param dir: directory to output the statistics and the matchings
    :return: None
    """
    with open(csv_file, encoding='utf-8', mode='r') as fin:
        G = read_course_allotment_graph(fin, skip_header, split_index)  # read the graph just once
        for i in range(iterations):
            stable_file = '{}/stable{}.txt'.format(dir, i)
            popular_file = '{}/popular{}.txt'.format(dir, i)
            stats_file = '{}/stats{}.txt'.format(dir, i)
            with tempfile.NamedTemporaryFile(dir=dir, suffix='.txt',
                                             prefix='graph{}_'.format(i), delete=False) as tmp_file:
                abs_pathname = tmp_file.name  # name of the graph file
                # write a random instance to a file
                print_course_allotment_graph(random_sample(graph.copy_graph(G)), tmp_file)
                G_r = graph_parser.read_graph(abs_pathname)  # read from the file
                matching_stats(G_r, stable_file, popular_file, stats_file)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate statistics from random instances of'
                                                 'student elective allocation graph')
    parser.add_argument('csv-file', help='path abs/relative of the csv file')
    parser.add_argument('dir', help='dir where the stats should be stored')
    parser.add_argument('--skip-header',  help='False if the csv header is not to be skipped '
                                               '(default: True)',
                        type=bool, default=True)
    parser.add_argument('--iterations', help='# of different random instances to compute '
                                             'statistics on (default: 10)',
                        type=int, default=10)
    parser.add_argument('--split-index', help='index where to split the row (default: 2)',
                        type=int, default=2)
    args = vars(parser.parse_args())  # parse the arguments

    # collect statistics
    collect_stats(csv_file=args['csv-file'], skip_header=args['skip_header'],
                  split_index=args['split_index'], iterations=args['iterations'], dir=args['dir'])

if __name__ == '__main__':
    main()
