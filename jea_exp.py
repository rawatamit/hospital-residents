#!/usr/bin/env python3

import os
import time
import subprocess
import collections

import sea
import sea2
import stats


CPPCODE_DIR = '/mnt/f55c6248-0895-4d46-8d0e-1db681847773/meghana/sea/GraphMatching/cmake-build-debug'


def recurse_directory(dirpath, filefn):
    """
    recurses over dirpath, and runs filefn on each file found
    """
    
    for entry in os.scandir(dirpath):
        if entry.is_file():
            filefn(entry)
        elif entry.is_dir():
            recurse_directory(entry.path, filefn)


def clean_directory(dirpath, fn):
    """
    deletes files recursively from dirpath which return true on fn
    fn takes a filename and not the filepath
    """

    filefn = lambda entry: os.remove(entry.path) and print(entry.name) if fn(entry.name) else None
    recurse_directory(dirpath, filefn)


def names_matching(*undesired, fn=lambda filename, pat: False):
    """
    returns a function which takes a filename and returns true if
    the filename matches any of the undesired patterns
    """

    return lambda filename: len([pat for pat in undesired if fn(filename, pat)]) > 0


def generate_matchings(entry, M_req):
    """
    output matchings specified in M_req for graph in entry
    """
    
    G_name = entry.name
    G_path = os.path.abspath(entry.path)
    dirpath = os.path.split(G_path)[0]

    # generate matchings that are needed
    for cppopt, mdesc in (('-s', sea.STABLE),
                          ('-p', sea.MAX_CARD_POPULAR),
                          ('-m', sea.POP_AMONG_MAX_CARD),
                          ('-h', sea.HRLQ_HHEURISTIC),
                          ('-e', sea.MAXIMAL_ENVYFREE)):
        if mdesc in M_req:
            print('working on', entry.path, 'computing', mdesc)
            start = time.time()
            mpath = os.path.join(dirpath, '{}{}'.format(mdesc, G_name))
            subprocess.run([os.path.join(CPPCODE_DIR, 'graphmatching'),
                            '-A', cppopt, '-i', G_path, '-o', mpath],
                            check=True)
            end = time.time()
            print('completed', mdesc, 'took', end - start, 's')


def compute_matchings(dirpath, matchings, ignore_fn):
    filefn = lambda entry: (None if ignore_fn(entry.name) else generate_matchings(entry, matchings))
    recurse_directory(dirpath, filefn)


def statistics_HR(dirpath, ignore_fn):
    matchings = (sea.STABLE, sea.MAX_CARD_POPULAR, sea.POP_AMONG_MAX_CARD)
    stats = collections.defaultdict(list)
    
    filefn = lambda entry: (None if ignore_fn(entry.name) else sea.generate_file_stats(entry, matchings, stats))
    recurse_directory(dirpath, filefn)
    return stats


def statistics_HRLQ(dirpath, ignore_fn):
    # generate stats
    sea2.generate_stats(dirpath)
    
    # print stats
    for dataset in ('shuffle', 'master', 'random'):
        dataset_dirpath = os.path.join(dirpath, dataset)
        outfile = os.path.join(dirpath, 'stats_{}.csv'.format(dataset))
    
        with open(outfile, mode='w', encoding='utf-8') as fout:
            stats.recurse_dir(dataset_dirpath, fout)


def run_experiments(dirpath, matchings, ignore_fn, statistics_fn):
    #clean_directory(dirpath, ignore_fn)
    #compute_matchings(dirpath, matchings, ignore_fn)
    return statistics_fn(dirpath, ignore_fn)


def run_experiments_HRLQ(dirpath):
    matchings = (sea.MAXIMAL_ENVYFREE,)
    ignore_fn = names_matching(*matchings, 'stats_',
                               fn=lambda filename, pat: filename.startswith(pat))
    return run_experiments(dirpath, matchings, ignore_fn, statistics_HRLQ)


def run_experiments_HR(dirpath):
    matchings = (sea.STABLE, sea.MAX_CARD_POPULAR, sea.POP_AMONG_MAX_CARD)
    ignore_fn = names_matching(*matchings, 'stats_', 'pdf', 'tex',
                               fn=lambda filename, pat: filename.startswith(pat) or filename.endswith(pat))
    return run_experiments(dirpath, matchings, ignore_fn, statistics_HR)


def average(stats):
    def avg(desc, data):
        '''
        average of particular desc
        M_p_vs_M_s or M_m_vs_M_s
        '''
        delta = 0
        delta_1 = 0
        delta_r = 0
        bp_m = 0
        M_s = 0
        n = len(data)

        for row in data:
            delta += row[desc]['delta']
            delta_1 += row[desc]['delta_1']
            delta_r += row[desc]['delta_r']
            bp_m += row[desc]['bp_m']
            M_s += row['S_M_s']

        return {'S_M_s': M_s/n, 'delta': delta/n, 'delta_1': delta_1/n, 'delta_r': delta_r/n, 'bp_m': bp_m/n}

    avg_stats = {}
    for k, v in stats.items():
        avg_stats[k] = {'M_p_vs_M_s': avg('M_p_vs_M_s', v), 'M_m_vs_M_s': avg('M_m_vs_M_s', v)}
    return avg_stats


if __name__ == '__main__':
    dirpath = '/mnt/f55c6248-0895-4d46-8d0e-1db681847773/meghana/sea/popular'
    new_db = '/mnt/f55c6248-0895-4d46-8d0e-1db681847773/meghana/newHR'

    HR_dirpath = os.path.join(dirpath, 'HR/shuffle')
    HRLQ_dirpath = os.path.join(dirpath, 'HRLQ')
    stats = run_experiments_HR(HR_dirpath)
    avg_stats = average(stats)

    for k, v in avg_stats.items():
        M_p_vs_M_s = v['M_p_vs_M_s']
        s1 = '{}&{}&{}&{}'.format(M_p_vs_M_s['delta'], M_p_vs_M_s['bp_m'], M_p_vs_M_s['delta_1'], M_p_vs_M_s['delta_r'])

        M_m_vs_M_s = v['M_m_vs_M_s']
        s2 = '{}&{}&{}&{}'.format(M_m_vs_M_s['delta'], M_m_vs_M_s['bp_m'], M_m_vs_M_s['delta_1'], M_m_vs_M_s['delta_r'])

        a = k.split(os.sep)
        print(a[-2], a[-1], stats[k][0]['R'], stats[k][0]['H'], M_m_vs_M_s['S_M_s'], s1, s2)
    #run_experiments_HRLQ(HRLQ_dirpath)
