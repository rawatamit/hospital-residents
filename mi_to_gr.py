import os
import sys
import graph


def readline(rdr):
    return rdr.readline().strip()


def read_graph(rdr):
    n_1 = int(readline(rdr))  # number of residents
    n_2 = int(readline(rdr))  # number of hospitals
    _ = readline(rdr)  # number of couples
    _ = readline(rdr)  # number of posts
    _ = readline(rdr)  # min resident pref list length
    _ = readline(rdr)  # max resident pref list length
    _ = readline(rdr)  # posts distributed evenly?
    _ = readline(rdr)  # resident popularity
    _ = readline(rdr)  # hospital popularity
    _ = readline(rdr)  # skip empty line

    # read the preferences of the residents
    A, E = set(), {}
    capacities = {}
    for i in range(n_1):
        data = readline(rdr).split()
        u = 'r{}'.format(data[0])
        # pref list for couples may contains duplicate
        # do not include them more than once in the original order
        pref_list = []
        for h in data[1:]:
            h_rep = 'h{}'.format(h)
            if h_rep not in pref_list:
                pref_list.append(h_rep)
        A.add(u)  # add this vertex to partition A
        E[u] = pref_list  # set its preference list
        capacities[u] = (0, 1)

    _ = readline(rdr)  # skip empty line

    # read the preferences of the hospitals
    B = set()
    for i in range(n_2):
        data = readline(rdr).split()
        u, capacity, = 'h{}'.format(data[0]), int(data[1])
        pref_list = ['r{}'.format(r) for r in data[2:]]
        B.add(u)  # add this vertex to partition B
        E[u] = pref_list  # set its preference list
        capacities[u] = (0, int(data[1]))

    return graph.BipartiteGraph(A, B, E, capacities)


def process_directory(indirpath, outdirpath):
    for entry in os.scandir(indirpath):
        outpath = os.path.join(outdirpath, ''.join(entry.name.split()))
        
        # write to our format
        with open(entry.path, encoding='utf-8', mode='r') as rdr:
            G = read_graph(rdr)
            with open(outpath, encoding='utf-8', mode='w') as out:
                out.write(graph.graph_to_UTF8_string(G))


def main():
    if len(sys.argv) < 3:
        print('usage: {} <indirpath> <outdirpath>'.format(sys.argv[0]))
    else:
        process_directory(sys.argv[1], sys.argv[2])


if __name__ == '__main__':
    main()
