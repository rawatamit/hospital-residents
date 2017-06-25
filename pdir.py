import os
import sys
import subprocess
import argparse
import sea
import graph_parser

CPPCODE_DIR='/home/amitrawt/Dropbox/projects/GraphMatching/build'


def generate_file_stats(in_dir_path, out_dir_path, G_name, req):
    G_path = os.path.join(os.path.abspath(in_dir_path), G_name)

    # remove vertices with empty preference list
    subprocess.run(['sed', '-i', '-E', '/^[[:lower:][:upper:][:digit:]]+ :  ;/d', G_path], check=True)

    # generate matchings that are needed
    matchings = {}
    for mdesc, cppopt, seadesc in (('H', '-h', sea.HRLQ_HHEURISTIC), ('S', '-s', sea.STABLE),
                                   ('P', '-p', sea.MAX_CARD_POPULAR), ('M', '-m', sea.POP_AMONG_MAX_CARD)):
        if mdesc in req:
            mpath = os.path.join(os.path.abspath(out_dir_path), '{}_{}'.format(mdesc, G_name))
            subprocess.run([os.path.join(CPPCODE_DIR, 'graphmatching'), '-A', cppopt,
                            '-i', G_path, '-o', mpath], check=True)
            matchings[seadesc] = sea.read_matching(mpath)

    # generate statistics for the files
    sea.generate_hr_tex(graph_parser.read_graph(G_path), matchings, out_dir_path, G_name)
    # sea.generate_heuristic_tex(graph_parser.read_graph(G_path), matchings, out_dir_path, G_name)


def generate_dir_stats(dir_path, req, rename=False):
    def is_graph_file(name):
        return ((not name.endswith('pdf')) and
                (not name.endswith('tex')) and
                (not name.startswith('S_')) and
                (not name.startswith('P_')) and
                (not name.startswith('M_')))

    # generate stats for every graph file in the given directory
    for entry in os.scandir(dir_path):
        if entry.is_file() and is_graph_file(entry.name):
            generate_file_stats(dir_path, dir_path, entry.name, req)


def main():
    parser = argparse.ArgumentParser(description='''Generate statistics in latex
                                format given a bipartite graph and matchings''')
    parser.add_argument('-D', dest='D', help='Dataset directory', required=True, metavar='')
    parser.add_argument('-S', dest='S', action='store_true', help='Generate stable matching')
    parser.add_argument('-P', dest='P', action='store_true', help='Generate max-cardinality popular matching')
    parser.add_argument('-M', dest='M', action='store_true', help='Generate popular among max-cardinality matchings')
    parser.add_argument('-H', dest='H', action='store_true', help='Generate heuristic matching for HRLQ')
    args = parser.parse_args()

    # generate statistics for the given matchings
    req = [mdesc for mdesc, mopt in [('H', args.H), ('S', args.S),
                                     ('P', args.P), ('M', args.M)] if mopt]
    generate_dir_stats(args.D, req, False)


if __name__ == '__main__':
    main()
