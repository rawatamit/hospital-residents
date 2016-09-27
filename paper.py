import matching_algos
import matching_stats
import random_instance
import os
import argparse


def collect_stats(graph_file, iterations, dir):
    """
    interface to the matching_stats function
    :param graph_file: abs/relative path to the graph file
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

    def G_fn():  # not used for now
        return random_instance.mahadian_k_model_generator(5000, 5000, 5)

    for n1 in (1000, 2000, 3000):# 10000, 20000, 30000, 50000, 100000):
        n2, cap = 30, int(20)
        for k in (5, 10):#, 15, 20, 25, 30):
            dir_path = '{}/n1_{}_k_{}'.format(dir, n1, k)
            os.makedirs(dir_path)
            matching_stats.collect_stats(lambda: random_instance.mahadian_k_model_generator_hospital_residents(n1, n2, k, cap),
                                         iterations, dir_path, matchings)


def main():
    parser = argparse.ArgumentParser(description='Generate statistics from random instances of'
                                                 'student elective allocation graph')
    parser.add_argument('graph-file', help='path abs/relative of the graph file')
    parser.add_argument('dir', help='dir where the stats should be stored')
    parser.add_argument('--iterations', help='# of different random instances to compute '
                                             'statistics on (default: 10)',
                        type=int, default=3)
    args = vars(parser.parse_args())  # parse the arguments

    # collect statistics
    collect_stats(graph_file=args['graph-file'], iterations=args['iterations'], dir=args['dir'])

if __name__ == '__main__':
    main()
