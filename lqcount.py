import graph
import graph_parser
import os
import sys


def lq_count(G):
    count = 0
    lq_sum = 0
    for h in G.B:
        if graph.lower_quota(G, h) > 0:
            lq_sum += graph.lower_quota(G, h)
            count += 1
    return count, lq_sum


def main():
    dirpath = sys.argv[1]
    for entry in os.scandir(dirpath):
        if entry.name.startswith('1000_') and entry.name.endswith('txt'):
            G = graph_parser.read_graph(entry.path)
            count, lq_sum = lq_count(G)
            print(entry.name, '# lq: {}, lq sum: {}'.format(count, lq_sum))

if __name__ == '__main__':
    main()

