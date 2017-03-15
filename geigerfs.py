#!/usr/bin/env python

from __future__ import with_statement, absolute_import

import sys
import time
import logging

from stat import S_IFDIR, S_IFREG
from errno import ENOENT
from sys import argv, exit
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

class GeigerFS(LoggingMixIn, Operations):
    def __init__(self):
        self.files = {}
        self.data = {}
        now = time.time()
        self.files['/'] = dict(st_mode=(S_IFDIR | 0o755), st_ctime=now,
                               st_mtime=now, st_atime=now, st_nlink=2)
        self.files['/random'] = dict(st_mode=(S_IFREG | 0o444), st_ctime=now,
                               st_mtime=now, st_atime=now, st_nlink=2)
        self.files['/cpm'] = dict(st_mode=(S_IFREG | 0o444), st_ctime=now,
                               st_mtime=now, st_atime=now, st_nlink=2)
        self.data['/random'] = ""
        self.data['/cpm'] = ""

    # Filesystem methods
    # ==================
    def getattr(self, path, fh=None):
        if path not in self.files:
            raise FuseOSError(ENOENT)
        
        return self.files[path]

    def read(self, path, length, offset, fh):
        return self.data[path][offset:offset + length]

    def readdir(self, path, fh):
        return ['.', '..'] + [x[1:] for x in self.files if x != '/']

    # Disable unused operations:
    access = None
    flush = None
    getxattr = None
    listxattr = None
    open = None
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
