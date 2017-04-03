#!/usr/bin/env python

from sys import argv
import time
import random

def main(filename, tsCount):
    t = time.time()
    fo = open(filename, 'w')
    for i in range(0, tsCount):
        t += random.random()
        fo.write(str(t) + '\n')
    fo.close()

if __name__ == '__main__':
    if len(argv) != 3:
        main("temp.txt", 99)
    else:
        main(argv[1], argv[2])

