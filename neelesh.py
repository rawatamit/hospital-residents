import graph
import graph_parser
import matching_algos
import csv
import collections
import random
import tempfile
from tabulate import tabulate


def read_course_allotment_graph(file, skip_header, split_index):
    """
    reads the course allotment graph from the given csv_file
    :param file: file having the graph in CSV format
    :param split_index: where to split a pref list
    :return: bipartite graph with the
    """
    # TODO: lot of hard coded values
    students, electives = set(), set()
    E = collections.defaultdict(list)  # dict to store the preference list

    # skip the header if needed
    if skip_header:
        file.readline()

    # read data
    for row in csv.reader(file):
        # FIXME: ugly code
        student_id, preferences = row[split_index-1], row[split_index:]

        # sanitize the preference list for the student
        pref_list, chosen = [], set()  # preferences already chosen by student
        for pref in preferences:
            if pref and pref not in chosen:  # only add non empty preferences
                chosen.add(pref)
                electives.add(pref)
                pref_list.append(pref)

        # do not add an isolated vertex, assume roll numbers are unique
        if pref_list:
            students.add(student_id)
            E[student_id] = pref_list

    capacities = dict((student, 1) for student in students)
    # TODO: fix this
    # cap = {'MA2010': 80, 'MA2020': 80, 'MA2030': 210, 'MA2040': 350}
    # cap = {'HS1100': 1, 'HS1120': 1, 'HS2200': 13, 'HS2320': 50,
    #       'HS3060': 4, 'HS3420': 4, 'HS4004': 21, 'HS4180': 11,
    #       'HS4330': 22, 'HS4370': 37, 'HS5612': 36, 'HS6140': 50}
    cap = {'HS1090': 60, 'HS2130': 26, 'HS2210': 106, 'HS2370': 53,
           'HS3002': 250, 'HS3005': 53, 'HS3007': 36, 'HS3029': 23,
           'HS4050': 53, 'HS4350': 25, 'HS4410': 50, 'HS4480': 45,
           'HS5080': 44, 'HS5920': 53, 'HS5930': 53, 'HS6130': 53,
           'HS7004': 41}
    capacities.update(cap)
    return graph.BipartiteGraph(students, electives, E, capacities)


def partial_shuffle(l, imin, imax):
    """
    partially shuffles a list
    :param l:
    :param imin:
    :param imax:
    :return:
    """
    l[imin:imax] = sorted(l[imin:imax], key=lambda x: random.random())
    return l


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

    # we need to know which all students have a elective
    # as their first preference, and who all have it as
    # a >1 preference, so we partition electives in two
    # categories

    # add the students who have elective as a first choice
    # to the electives pref list before any other which
    # has it as a >1 preference
    # to keep track of how many residents provide the
    # hospital as the first preference, we use pref1
    pref1 = collections.defaultdict(int)
    for student in G.A:
        E[E[student][0]].append(student)
        pref1[E[student][0]] += 1

    # add all the electives, remember that elective #0 for
    # every student has already been added
    for student in G.A:
        for i in range(1, len(E[student])):
            elective = E[student][i]
            E[elective].append(student)

    # shuffle the preference list for the electives
    for elective in G.B:
        partial_shuffle(E[elective], pref1[elective], len(E[elective]))

    return graph.BipartiteGraph(G.A, G.B, E, G.capacities)


def print_course_allotment_graph(G, gfile):
    """
    prints the graph to a file
    :param G: bipartite graph
    :param gfile: file path to write graph to
    :return: None
    """
    with open(gfile, mode='w', encoding='utf-8') as out:
        out.write(graph.graph_to_UTF8_string(G))


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


def matching_stats(G, max_card_file, stable_file, popular_file, stats_file):
    """
    prints the matchings and the stats generated
    :param G: bipartite graph
    :param max_card_file: file to output the max card matching
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

    def avg(l):
        return sum(l) / len(l)

    # generate the max card matching
    M_max_card = matching_algos.max_card_matching(graph.copy_graph(G))
    # write it to the file
    print_matching(G, M_max_card, max_card_file)

    # generate the stable matching
    M_stable = matching_algos.stable_matching_hospital_residents(graph.copy_graph(G))
    # write it to the file
    print_matching(G, M_stable, stable_file)

    # the popular matching
    M_popular = matching_algos.popular_matching_hospital_residents(G)
    # write it to the file
    print_matching(G, M_popular, popular_file)

    # print some stats corresponding to the matchings obtained
    with open(stats_file, encoding='utf-8', mode='w') as fout:
        indices_mc = [G.E[a].index(M_max_card[a])+1 for a in G.A if a in M_max_card]
        indices_stable = [G.E[a].index(M_stable[a])+1 for a in G.A if a in M_stable]
        indices_popular = [G.E[a].index(M_popular[a])+1 for a in G.A if a in M_popular]

        table = (['matching desc.', 'matching size', '# unstable pairs',
                  'min index', 'max index', 'avg index'],
                 ['max_card', nmatched_pairs(M_max_card), len(matching_algos.unstable_pairs(G, M_max_card)),
                  min(indices_mc), max(indices_mc), avg(indices_mc)],
                 ['stable', nmatched_pairs(M_stable), len(matching_algos.unstable_pairs(G, M_stable)),
                  min(indices_stable), max(indices_stable), avg(indices_stable)],
                 ['popular', nmatched_pairs(M_popular), len(matching_algos.unstable_pairs(G, M_popular)),
                  min(indices_popular), max(indices_popular), avg(indices_popular)])
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
            max_card_file = '{}/max_card{}.txt'.format(dir, i)
            stable_file = '{}/stable{}.txt'.format(dir, i)
            popular_file = '{}/popular{}.txt'.format(dir, i)
            stats_file = '{}/stats{}.txt'.format(dir, i)
            with tempfile.NamedTemporaryFile(dir=dir, suffix='.txt',
                                             prefix='graph{}_'.format(i), delete=False) as tmp_file:
                abs_pathname = tmp_file.name  # name of the graph file
                # write a random instance to a file
                G_r = random_sample(G)
                print_course_allotment_graph(G_r, abs_pathname)
                # G_r = graph_parser.read_graph(abs_pathname)  # read from the file
                matching_stats(G_r, max_card_file, stable_file, popular_file, stats_file)


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
