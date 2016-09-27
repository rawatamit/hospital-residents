import graph
import matching_algos
import matching_stats
import csv
import collections
import random
import argparse


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
    #print(electives)
    # TODO: fix this
    # cap = {'MA2010': 80, 'MA2020': 80, 'MA2030': 210, 'MA2040': 350}
    # cap = {'HS1100': 1, 'HS1120': 1, 'HS2200': 13, 'HS2320': 50,
    #       'HS3060': 4, 'HS3420': 4, 'HS4004': 21, 'HS4180': 11,
    #       'HS4330': 22, 'HS4370': 37, 'HS5612': 36, 'HS6140': 50}
    # original capacities for slot F
    # cap = {'HS1090': 60, 'HS2130': 26, 'HS2210': 106, 'HS2370': 53,
    #       'HS3002': 250, 'HS3005': 53, 'HS3007': 36, 'HS3029': 23,
    #       'HS4050': 53, 'HS4350': 25, 'HS4410': 50, 'HS4480': 45,
    #       'HS5080': 44, 'HS5920': 53, 'HS5930': 53, 'HS6130': 53,
    #       'HS7004': 41}
    # cap = {'HS1090': 45, 'HS2130': 20, 'HS2210': 80, 'HS2370': 40,
    #        'HS3002': 188, 'HS3005': 40, 'HS3007': 27, 'HS3029': 18,
    #        'HS4050': 40, 'HS4350': 19, 'HS4410': 38, 'HS4480': 34,
    #        'HS5080': 33, 'HS5920': 40, 'HS5930': 40, 'HS6130': 40,
    #        'HS7004': 31}
    #cap = {'HS1060': 50, 'HS2030': 50, 'HS2370': 50, 'HS3002A': 60,
    #       'HS3002B': 60, 'HS3002C': 60, 'HS3002D': 70, 'HS3420': 96,
    #       'HS4002': 50, 'HS4070': 50, 'HS4540': 50, 'HS5920': 50,
    #       'HS5930': 50}
    cap1 = {'HS1090': 20,#10,
    'HS1090+': 20,#50,
    'HS1110': 20,
    'HS2050': 20,
    'HS3002': 20,
    'HS3002A': 20,
    'HS3002B': 20,
    'HS3002C': 20,
    'HS3002D': 20,
    'HS3280': 20,
    'HS3420A': 20,
    'HS4002': 20,
    'HS4540': 20,
    'HS5070': 20,
    'HS5920': 20,
    'HS5930': 20,
    'HS4005': 20,
    'HS4006': 20}
    cap = {'MA2010': 85,
            'MA2020': 560,
            'MA2031': 140,
            'MA2040': 80,
            'MA2130': 85,
            'PH2170': 50,
            'PH3500': 50}

    capacities.update(cap)
    return graph.BipartiteGraph(students, electives, E, capacities)


def partial_shuffle(l, start, end):
    """
    partially shuffles a list, taken from
    http://stackoverflow.com/questions/27343932/how-to-random-shuffle-slice-or-subset-of-list-of-objects?lq=1
    :param l: list
    :param start: start index
    :param end: end index, not included
    :return: list with l[start:end] shuffled
    """
    l[start:end] = sorted(l[start:end], key=lambda x: random.random())
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
        for elective in pref_list:
            E[elective].append(student)

    for elective in G.B:
        random.shuffle(G.E[elective])
    return graph.BipartiteGraph(G.A, G.B, E, G.capacities)


def collect_stats(csv_file, skip_header, split_index, iterations, dir):
    """
    interface to the matching_stats function
    :param csv_file: graph in CSV format
    :param iterations: # of different random instances to run on
    :param dir: directory to output the statistics and the matchings
    :return: None
    """
    matchings = [{'desc': 'max_card',
                  'algo': matching_algos.max_card_hospital_residents,
                  'file': lambda dir, iteration: '{}/max_card{}.txt'.format(dir, iteration)},
                 {'desc': 'stable',
                  'algo': matching_algos.stable_matching_hospital_residents,
                  'file': lambda dir, iteration: '{}/stable{}.txt'.format(dir, iteration)},
                 {'desc': 'popular',
                  'algo': matching_algos.popular_matching_hospital_residents,
                  'file': lambda dir, iteration: '{}/popular{}.txt'.format(dir, iteration)}]

    with open(csv_file, encoding='utf-8', mode='r') as fin:
        G = read_course_allotment_graph(fin, skip_header, split_index)  # read the graph just once

        def G_fn():
            return random_sample(G)
        matching_stats.collect_stats(G_fn, iterations, dir, matchings)


def main():
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
