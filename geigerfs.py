#!/usr/bin/env python

from __future__ import with_statement, absolute_import

import time
import logging
import os
import math
import random

from stat import S_IFDIR, S_IFREG, S_IFCHR
from errno import ENOENT
from sys import argv, exit
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

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
                               st_mtime=now, st_atime=now, st_nlink=1)
        self.files['/cpm'] = dict(st_mode=(S_IFREG | 0o444), st_ctime=now,
                               st_mtime=now, st_atime=now, st_nlink=1,
                               st_size=3)

        self.reads['/cpm'] = self.doReadCpm
        self.reads['/random'] = self.doReadRandom
        self.fileName = harvestFile
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

	# write pseudorandom bytes to the path file  
	for i in range(length):
		try:			
			number = int(math.floor((random.random() * 256)))   # convert random
			self.data[path].append(number)                      # float to byte
		except: pass
	
	# write new 4 byte seed back to the pseudo file
	f.seek()   # go to pseudo file beginning
	for i in range(4):
		number = int(math.floor((random.random() * 256))) 
		f.write(number)
	tfh.close()
        return

    def doReadRandom(self, path, length, offset, fh):
        return self.data[path][offset:offset + length]

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
