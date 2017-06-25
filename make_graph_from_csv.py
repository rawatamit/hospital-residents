#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 24 15:15:17 2017

@author: amitrawt
"""


import sys
import csv
import copy
import graph


def read_csv(filename, fn):
    with open(filename, mode='r', encoding='utf-8') as rdr:
        return fn(csv.reader(rdr))


def read_student_preferences(rdr):
    return {row[0]: row[1:] for row in rdr}


def read_course_preferences(rdr):
    return {row[0]: row[1:] for row in rdr}


def read_course_capacities(rdr):
    return {row[0]: (0, int(row[2])) for row in rdr}


def make_graph(student_preferences, course_preferences, course_capacities):
    cap = course_capacities
    cap.update(dict((student, (0, 1)) for student in student_preferences.keys()))
    E = copy.copy(student_preferences)
    E.update(course_preferences)
    return graph.BipartiteGraph(student_preferences.keys(), course_preferences.keys(), E, cap)


def main():
    if len(sys.argv) < 4:
        print('usage: {} student_pref course_pref course_list'.format(sys.argv[0]), file=sys.stderr)
    else:
        student_preferences_file = sys.argv[1]
        course_preferences_file = sys.argv[2]
        course_list_file = sys.argv[3]
        student_preferences = read_csv(student_preferences_file, read_student_preferences)
        course_preferences = read_csv(course_preferences_file, read_course_preferences)
        course_capacities = read_csv(course_list_file, read_course_capacities)
        G = make_graph(student_preferences, course_preferences, course_capacities)
        print(graph.graph_to_UTF8_string(G))


if __name__ == '__main__':
    main()
