#! /usr/bin/env python

import random
import sys

topics = ['planned', 'happened', 'went well', 'went badly',
          'possible improvements', 'safe space', 'Recap', 'Parking Lot']


def assign_mods(attendees):
    n = []
    for i in range(len(topics)/len(attendees)):
        n += random.sample(attendees, len(attendees))
    if len(topics) % len(attendees) != 0:
        n += random.sample(attendees, len(topics) % len(attendees))
    return zip(topics, n)


if __name__ == "__main__":

    attendees = ['fbo', 'nhicher', 'tristanC', 'jpena', 'dms',
                 'mhu', 'jruzicka', 'pabelanger', 'ianw']
    if len(sys.argv) > 1:
        if len(sys.argv) == 2:
            if sys.argv[1] in ["--help", "-h"]:
                print("'%s NAME1 ... NAMEn' or \n" % sys.argv[0] +
                      "'%s NAME1,...,NAMEn' or \n" % sys.argv[0] +
                      "'%s'\n\n" % sys.argv[0])
                sys.exit(0)
            attendees = sys.argv[1].split(',')
        else:
            attendees = sys.argv[1:]

    for i, j in assign_mods(attendees):
        print("%s: %s" % (i, j))
