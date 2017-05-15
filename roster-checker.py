#!/usr/local/bin/python3
#
# roster-checker.py
# cs1570-grader
#
# Created by Illya Starikov on 05/14/17.
# Copyright 2017. Illya Starikov. All rights reserved.
#

import sys
import csv
import os
from pprint import pprint


def printError(error):
    sys.stdout = sys.stderr
    print(error)
    sys.exit(1)


def parseRosterFile(filename):
    students = []
    with open(filename, 'rt') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        for row in csvreader:
            students += row

    return students


def parseStudentFiles(filename):
    return os.listdir(filename)


def stringIsSubstringInArray(string, array):
    for element in array:
        if string in element or element in string:
            return True

    return False


def removeOverlap(toRemove, toCheckAgainst):
    return list(filter(lambda x: not stringIsSubstringInArray(x, toCheckAgainst), toRemove))


def main():
    if len(sys.argv) < 3:
        printError("usage: python3 stylechecker.py PATH/TO/ROSTER/FILE PATH/TO/STUDENTS/DIRECTORY/")

    rosterPath = sys.argv[1]
    roster = parseRosterFile(rosterPath)

    studentPath = sys.argv[2]
    students = parseStudentFiles(studentPath)

    rosterRemovedFromDirectory = removeOverlap(roster, students)
    diretoryRemovedFromRoster = removeOverlap(students, roster)

    if diretoryRemovedFromRoster:
        print("Wrong Submission")
        pprint(diretoryRemovedFromRoster)

    if rosterRemovedFromDirectory:
        print("Has Yet To Submit")
        pprint(rosterRemovedFromDirectory)


if __name__ == "__main__":
    main()
