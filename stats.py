#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os


SIZE = 'size'
BPAIRS = '# blocking pair'
BRES = '# blocking residents'
RANK1RES = '# residents matched to rank-1 partners'
DEF = 'total deficiency'


def parse_stats(s):
    return {stat.split(':')[0]: stat.split(':')[1] for stat in s.split('\n') if stat}


def print_stats(filepath, filename, fout):
    with open(filepath, mode='r', encoding='utf-8') as fin:
        filestat = parse_stats(fin.read())
        print(','.join([filename[6:], filestat[SIZE], filestat[BPAIRS],
                       filestat[BRES], filestat[RANK1RES], filestat[DEF]]), file=fout)


def recurse_dir(dirpath, fout):
    for entry in os.scandir(dirpath):
        if entry.is_file() and entry.name.startswith('stats_'):
            print_stats(entry.path, entry.name, fout)
        elif entry.is_dir():
            print(',{},{},{},{},{}'.format(SIZE, BPAIRS, BRES, RANK1RES, DEF), file=fout)
            print('{},,,,'.format(entry.name), file=fout)
            recurse_dir(entry.path, fout)
            print('\n\n', file=fout)


if __name__ == '__main__':
    TOPLEVELDIR = '/mnt/f55c6248-0895-4d46-8d0e-1db681847773/meghana/sea/popular/HRLQ'
    for dataset in ('shuffle', 'master', 'random'):
        dirpath = os.path.join(TOPLEVELDIR, dataset)
        outfile = os.path.join(TOPLEVELDIR, '{}-stats.csv'.format(dataset))
    
        with open(outfile, mode='w', encoding='utf-8') as fout:
            recurse_dir(dirpath, fout)
