#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 18:54:24 2017

@author: Amit Rawat
"""

import graph_parser
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def rank_matrix(G, U, V):
    '''
    :param G: bipartite graph
    :param U: rows of the matrix
    :param V: the partition which ranks the vertices in U
    '''
    # there are |U| rows and max(len(G.E[v])) columns
    ncols = max(len(G.E[v]) for v in V)
    mat = pd.DataFrame(0, index=U, columns=np.arange(1, ncols+1))

    # fill in the values
    for v in V:
        for i in range(len(G.E[v])):
            u = G.E[v][i]
            mat.loc[u, i+1] += 1

    return mat


def avg_rank(U, mat):
    avg = []

    for u in U:
        den = mat.loc[u].sum()
        num = sum(k * mat.loc[u, k] for k in mat.columns)
        avg.append((u, num/den))

    return sorted(avg, key=lambda x: x[1])


def generate_line_plot(xlabel, ylabel, xaxis, yaxis, filename):
    # start with a clean figure
    plt.clf()
    plt.figure(figsize=(7, 6))

    # set the x and y labels
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.plot(xaxis, yaxis)

    # legend
    # plt.legend(loc='best')
    plt.savefig(filename)


def main():
    # dirpath = '/home/amitrawt/Dropbox/projects/matching/tests+data/hand-crafted'
    dirpath = '/media/amitrawt/5073c06b-f306-4e3a-9e18-23d2c9921453/ms_project/MIN_BP/couples/Experiment3'
    # dirpath = '/home/amitrawt/Dropbox/SEA2017/dataset/HR/mahdian_prob_ml/n1_1000_n2_100_k_5'
    # dirpath = '/home/amitrawt/Dropbox/SEA2017/dataset/HR/mrandom/n1_1000_n2_100_k_5'
    # dirpath = '/home/amitrawt/Dropbox/projects/matching/n1_100_n2_10_k_5'
    # G = graph_parser.read_graph(os.path.join(dirpath, '1000_10_5_100_1.txt'))
    files = ['100-10-10-100-3-5-false-5-5-Iteration1.txt', '100-10-10-100-3-5-false-5-5-Iteration2.txt',
             '100-10-10-100-3-5-false-5-5-Iteration3.txt']
    # files = ['1000_100_5_10_1.txt', '1000_100_5_10_2.txt', '1000_100_5_10_3.txt']
    #files = ['100_10_5_10_1.txt', '100_10_5_10_2.txt', '100_10_5_10_3.txt']

    for filename in files:
        filepath = os.path.join(dirpath, filename)
        G = graph_parser.read_graph(filepath)
        mat_h = rank_matrix(G, G.B, G.A)
        avg_h = avg_rank(G.B, mat_h)
        generate_line_plot('H', 'avg rank',
                           range(0, len(avg_h)), [p for _, p in avg_h],
                           'H_{}.png'.format(filename))

        mat_r = rank_matrix(G, G.A, G.B)
        avg_r = avg_rank(G.A, mat_r)
        generate_line_plot('R', 'avg rank',
                           range(0, len(avg_r)), [p for _, p in avg_r],
                           'R_{}.png'.format(filename))

if __name__ == '__main__':
    main()
