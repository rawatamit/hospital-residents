import graph
import matching_utils
from tabulate import tabulate


def print_graph(G, gfile):
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
    # max_credits, course_credits = 10, 10
    with open(filename, mode='w', encoding='utf-8') as out:
        for student in G.A:
            if student in M:  # only if the student has been alloted to a course
                h = M[student]
                print('{},{},{}'.format(
                    student,  # max_credits,
                    h,  # course_credits,
                    G.E[student].index(h) + 1), file=out)


def process_stats(G, dir, iteration, stats_file_name, matchings):
    """
    prints the matchings and the stats generated
    :param G: bipartite graph
    :param dir: directory to output the stats/matchings to
    :param iteration: iteration #
    :param stats_file_name: function to generate name for the stat file
    :param matchings: see documentation for collect_stats
    :return: None
    """
    # TODO: fix the utility functions below,
    # before running on a hospital-residents instance
    # all of them require changes
    def nmatched_pairs(M):
        """
        :param M: valid matching in G
        :return: # of matched pairs in M
        """
        return sum(len(M[h]) for h in G.B if h in M)

    def avg(l):
        return sum(l) / len(l)

    def get_indices(M):
        return [G.E[a].index(M[a])+1 for a in G.A if a in M]

    # generate and print the matchings
    table = [['matching desc.', 'matching size', '# unstable pairs',
              'min index', 'max index', 'avg index']]
    for matching in matchings:
        M = matching['algo'](graph.copy_graph(G))
        # print(M)
        indices = get_indices(M)
        table.append([matching['desc'], nmatched_pairs(M), len(matching_utils.unstable_pairs(G, M)),
                      min(indices), max(indices), avg(indices)])
        print_matching(G, M, matching['file'](dir, iteration))

    # print the stats corresponding to the matchings obtained
    with open(stats_file_name(dir, iteration), encoding='utf-8', mode='w') as fout:
        print(tabulate(table, headers='firstrow', tablefmt='psql'), file=fout)


def collect_stats(G_fn, iterations, dir, matchings):
    """
    interface to the matching_stats function
    :param G_fn: a function which returns a graph every invocation
    :param iterations: # of different random instances to run on
    :param dir: directory to output the statistics and the matchings
    :param matchings: list of dictionaries which contains information
                      about the matching to be computed, like description,
                      algorithm, and file to generate output to
    :return: None
    """
    def stats_file_name(dir, iteration):
        return '{}/stats{}.txt'.format(dir, iteration)

    for iteration in range(iterations):
        G = G_fn()  # get a graph instance
        gfile = '{}/graph{}.txt'.format(dir, iteration)
        print_graph(G, gfile)
        # G_r = graph_parser.read_graph(abs_pathname)  # read from the file
        process_stats(G, dir, iteration, stats_file_name, matchings)
