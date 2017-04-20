#!/usr/bin/env python

from __future__ import with_statement, absolute_import

import time
import logging
import os
import math
import random
import fileinput

from collections import deque
from stat import S_IFDIR, S_IFREG, S_IFCHR
from errno import ENOENT
from sys import argv, exit, stdout
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
from bitarray import bitarray

class GeigerFS(LoggingMixIn, Operations):
    def __init__(self, harvestFile='times.txt', pseudoFile='pseudo.txt'):
        self.files = {} # file stats for each vfile
        self.data = {}  # data str for each vfile
        self.reads = {} # handlers for the read operation for each vfile
        self.timesfhs = {}  # file handles for the times.txt file for each vfile

        now = time.time()
        self.data['/random'] = ""
        self.data['/cpm'] = "0"
        self.files['/'] = dict(st_mode=(S_IFDIR | 0o755), st_ctime=now,
                               st_mtime=now, st_atime=now, st_nlink=2)
        self.files['/random'] = dict(st_mode=(S_IFREG | 0o444), st_ctime=now,
                               st_mtime=now, st_atime=now, st_nlink=1, st_size=4096)
        self.files['/cpm'] = dict(st_mode=(S_IFREG | 0o444), st_ctime=now,
                               st_mtime=now, st_atime=now, st_nlink=1,
                               st_size=4096)

        self.reads['/cpm'] = self.doReadCpm
        self.reads['/random'] = self.doReadRandom
        self.fileName = harvestFile
        self.h_fn_bak = harvestFile + ".bak"
        self.pseudoFN = pseudoFile

    # Filesystem methods
    # ==================
    def getattr(self, path, fh=None):
        if path not in self.files:
            raise FuseOSError(ENOENT)

        self.files[path]['st_ctime'] = os.stat(self.fileName).st_ctime
        self.files[path]['st_mtime'] = os.stat(self.fileName).st_mtime
        self.files[path]['st_atime'] = os.stat(self.fileName).st_atime

        return self.files[path]

    def read(self, path, length, offset, fh):
        return self.reads[path](path, length, offset, fh)

    def readdir(self, path, fh):
        return ['.', '..'] + [x[1:] for x in self.files if x != '/']

    def open(self, path, flags):
        self.timesfhs[path] = open(self.fileName, 'r+')
        return Operations.open(self, path, flags)

    def doReadCpm(self, path, length, offset, fh):
        ''' returns the count of events detected per minute '''
        cpm = 0         # final calculated counts per minute
        accum_cpm = 0   # accumulating counts per minute
        last_ts = 0.0   # the last time stamp in the time stamps file
        tfh = self.timesfhs[path]   # get the file handle to the times file for this instance
        times_offset = 1024     # initial offset from for reading from the end of the file
        time_diff = 0   # time difference from intervals
        is_at_end_of_file = False   # have we ended up reading the whole file

        # Read in increments of 1k chunks until we read the whole file,
        # or we get a minute's worth of events.
        while ((not is_at_end_of_file) and time_diff < 60):
            # Check to see if file is larger than current offset for times file:
            if (os.path.getsize(self.fileName) > times_offset):
                tfh.seek(-times_offset, os.SEEK_END)
                tstamps = tfh.readlines()
                del tstamps[0]  # remove first element since it might be a partial time stamp
            else:   # otherwise read the whole file
                tstamps = tfh.readlines()
                is_at_end_of_file = True
            if (last_ts == 0.0):    # get the latest time stamp once
                try: last_ts = float(tstamps[-1])
                except: pass
            for ts in reversed(tstamps):    # for each time stamp going backwards
                try:
                    if ( not ts ):
                        break
                    else:
                        time_diff = last_ts - float(ts)
                    if (time_diff < 60.0):
                        accum_cpm += 1
                    else:
                        break   # go until we reach a minute
                except ValueError:
                    logging.exception('')
            times_offset += 1024
            cpm = accum_cpm
            accum_cpm = 0
        self.data[path] = str( cpm ) + '\n'
        return self.data[path][offset:offset + length]

    def doPseudoRead(self, path, length, offset):
        ''' ...generates random bytes when times.txt is empty... '''
        # get 4 byte seed from pseudo file
        tfh = open(self.pseudoFN, 'r+')
        seed = tfh.read(4)
        random.seed(seed)

        # write pseudo random bytes to the path file
        for i in range(length):
            try:
                number = chr(int(math.floor(random.random() * 256)))   # convert random
                self.data[path] += number + '\n'                       # float to byte
            except: pass

        # write new 4 byte seed back to the pseudo file
        tfh.seek(0)   # go to pseudo file beginning
        for i in range(4):
            number = chr(int(math.floor(random.random() * 256)))
            tfh.write(number)
        tfh.close()
        return

    def doReadRandom(self, path, length, offset, fh):
        lines_to_read = (length * 8) + 1
        i = lines_to_read
        a = bitarray()              # create empty bitarray
        tstamps = deque()
        h_bak = open(self.h_fn_bak, 'w')
        tfh = self.timesfhs[path]   # get the file handle to the times file for this instance
        tfh.seek(0)                 # reseek if called before
        for l in range(3):
            line = tfh.readline()
            if not line:
                return self.doPseudoRead(path, length, offset)
            tstamps.append(line)
        while (line):
            if i <= 1:
                h_bak.write(line)   # done reading timestamps for random number, write the rest of the lines
                line = tfh.readline()
            else:
                interval_one = float(tstamps[1])-float(tstamps[0])  #calculate time stamp diffs
                interval_two = float(tstamps[2])-float(tstamps[1])
                if(interval_one < interval_two):
                    a.append(False)                             # i think both boolean  or binary values work here for bitarrays
                else:
                    a.append(True)
                i -= 1
                tstamps.rotate(-1)
                line = tfh.readline()
                if line:
                    tstamps[2] = line

        if i > 1:
            fsize = 0
            try:
                fsize = os.path.getsize(self.pseudoFN)
            except OSError as detail:
                logging.error(detail)
            if fsize == 0:
                return ""
            elif fsize < 4:
                with open(self.pseudoFN, 'a') as pfh:
                    pfh.write(a.tobytes()[:fsize-4])
            return self.doPseudoRead(path, length, offset)
        else:
            h_bak.close()
            tfh.close()
            os.rename(self.h_fn_bak, self.fileName)
            self.timesfhs[path] = open(self.fileName, 'r+')
            return a.tobytes()

    # Disable unused operations:
    access = None
    flush = None
    getxattr = None
    listxattr = None
    opendir = None
    release = None
    releasedir = None
    statfs = None

if __name__ == '__main__':
    if len(argv) != 2:
        print('usage: %s <mountpoint>' % argv[0])
        exit(1)
        
    logging.basicConfig(level=logging.DEBUG)
    
    FUSE(GeigerFS(), argv[1], nothreads=True, foreground=True, ro=True)
