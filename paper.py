import graph
import graph_parser
import matching_algos
import collections
import random
from tabulate import tabulate


def random_sample(G):
    """
    generates a random sampling, which is then returned
    as a bipartite graph, from the given graph
    the returned preference lists are symmetric
    :param G: bipartite graph
    :return: bipartite graph from a random sample
    """
    def order_by_master_list(l, master_list):
        return sorted(l, key=master_list.index)

    # prepare a master list
    master_list = list(h for h in G.B)
    random.shuffle(master_list)

    E = collections.defaultdict(list)  # to store the new sampled preference list
    for resident in G.A:
        pref_list = G.E[resident]
        E[resident] = order_by_master_list(pref_list[:], master_list)
        # for all the hospitals add the students to their preference list
        for hospital in pref_list:
            E[hospital].append(resident)

    # shuffle the preference list for the hospitals
    for hospital in G.B:
        random.shuffle(E[hospital])

    return graph.BipartiteGraph(G.A, G.B, E, G.capacities)


def print_matching(G, M, filename):
    """
    prints the matching in the following format to the file:
    resident, hospital, index in the pref list
    :param G: bipartite graph
    :param M: matching in G
    :param filename: file to write to
    :return: None
    """
    with open(filename, mode='w', encoding='utf-8') as out:
        for resident in G.A:
            if resident in M:  # only if the resident has been alloted to a hospital
                hospital = M[resident]
                out.write('{},{},{}\n'.format(
                           resident, hospital, G.E[resident].index(hospital) + 1))


def matching_stats(G, max_card_file, stable_file, popular_file, stats_file):
    """
    prints the matchings and the stats generated
    :param G: bipartite graph
    :param stable_file: file to output the max card matching
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
    M_popular = matching_algos.popular_matching_hospital_residents(graph.copy_graph(G))
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


def collect_stats(graph_file, iterations, dir):
    """
    interface to the matching_stats function
    :param graph_file: abs/relative path to the graph file
    :param iterations: # of different random instances to run on
    :param dir: directory to output the statistics and the matchings
    :return: None
    """
    G = graph_parser.read_graph(graph_file)
    for i in range(iterations):
        G_r = random_sample(graph.copy_graph(G))
        max_card_file = '{}/max_card{}.txt'.format(dir, i)
        stable_file = '{}/stable{}.txt'.format(dir, i)
        popular_file = '{}/popular{}.txt'.format(dir, i)
        stats_file = '{}/stats{}.txt'.format(dir, i)
        with open('{}/graph{}.txt'.format(dir, i), mode='w', encoding='utf-8') as gout:
            print(graph.graph_to_UTF8_string(G_r), file=gout)
            matching_stats(G_r, max_card_file, stable_file, popular_file, stats_file)


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
