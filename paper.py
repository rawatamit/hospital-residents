import graph
import matching_algos
import matching_stats
import random_instance
import collections
import random


def random_sample(G):
    """
    generates a random sampling, which is then returned
    as a bipartite graph, from the given graph
    the returned preference lists are symmetric
    :param G: bipartite graph
    :return: bipartite graph from a random sample
    """
    E = collections.defaultdict(list)  # to store the new sampled preference list
    for resident in G.A:
        pref_list = G.E[resident]
        E[resident] = pref_list
        # for all the hospitals add the students to their preference list
        for hospital in pref_list:
            E[hospital].append(resident)

    # shuffle the preference list for the hospitals
    for hospital in G.B:
        random.shuffle(E[hospital])
    return graph.BipartiteGraph(G.A, G.B, E, G.capacities)


def collect_stats(graph_file, iterations, dir):
    """
    interface to the matching_stats function
    :param graph_file: abs/relative path to the graph file
    :param iterations: # of different random instances to run on
    :param dir: directory to output the statistics and the matchings
    :return: None
    """
    matchings = [{'desc': 'max_card',
                  'algo': matching_algos.max_card_man_woman,
                  'file': lambda dir, iteration: '{}/max_card{}.txt'.format(dir, iteration)},
                 {'desc': 'stable',
                  'algo': matching_algos.stable_matching_man_woman,
                  'file': lambda dir, iteration: '{}/stable{}.txt'.format(dir, iteration)},
                 {'desc': 'popular',
                  'algo': matching_algos.popular_matching_man_woman,
                  'file': lambda dir, iteration: '{}/popular{}.txt'.format(dir, iteration)}]

    def G_fn():
        return random_instance.generate_random_graph(5000, 5000, 5, 1)

    for i in range(iterations):
        matching_stats.collect_stats(G_fn, iterations, dir, matchings)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate statistics from random instances of'
                                                 'student elective allocation graph')
    parser.add_argument('graph-file', help='path abs/relative of the graph file')
    parser.add_argument('dir', help='dir where the stats should be stored')
    parser.add_argument('--iterations', help='# of different random instances to compute '
                                             'statistics on (default: 10)',
                        type=int, default=10)
    args = vars(parser.parse_args())  # parse the arguments

    # collect statistics
    collect_stats(graph_file=args['graph-file'], iterations=args['iterations'], dir=args['dir'])

if __name__ == '__main__':
    main()
