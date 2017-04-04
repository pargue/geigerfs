#!/usr/bin/env python  
# -*- coding: utf-8 -*-  
import errno  
import fuse  
import stat  
import time  
import os,sys,glob
import hashlib
import pickle


fuse.fuse_python_api = (0, 2)  
  
class MyFS(fuse.Fuse):  

    def __init__(self, *args, **kw):  
	for x in sys.argv:
		print "***"+x
	print ":::::"+sys.argv[-2]
	self.open_files = {}
	self.hard_links = pickle.load(open(sys.argv[-2]+"/.tbfs_hard_links","rb"))
        fuse.Fuse.__init__(self, *args, **kw)  

    def getattr(self, path):  

	print "getattr-path: ",path
        return os.stat(sys.argv[-2]+path)

    def readdir(self,path,offset):
	print "*** READDIR: ",path

	yield fuse.Direntry('.')
	yield fuse.Direntry('..')
	print ":::::"+sys.argv[-2]
	for x in os.listdir(sys.argv[-2]+path):
		yield fuse.Direntry(os.path.basename(x))

#	yield fuse.Direntry('test')

	return
	
	

    def open(self,path,flags):

	print "********* OPEN: ",path

	access_flags = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
	access_flags = flags & access_flags

	if access_flags == os.O_RDONLY:
		fi=open(sys.argv[-2]+path,"rb")
		self.open_files[path]=fi
		return 0

	else: 			#access_flags == os.O_WRONLY:

		fi=open(sys.argv[-2]+path,"wb")
		self.open_files[path]=fi
		return 0


	return -errno.EACCESS

    def create(self, path, flags, mode):

	print "****CREATE: ",path
	fi=open(sys.argv[-2]+path,"w")
        self.open_files[path]=fi
        return 0

    def chmod(self, path, mode):
	print "*****CHMOD: ",path

	return 0

    def read(self,path,size,offset):

	print "****READ********: ",path,size,offset

	fi=self.open_files[path]
	fi.seek(offset)

	return fi.read(size)


    def write(self,path, buf, offset, fh=None):

	print "***WRITE: ",path,offset	

	fo=self.open_files[path]
	fo.seek(offset)
	fo.write(buf)
	return len(buf)

    def flush(self, path, fh=None):

	print "***FLUSH: ",path

	if path in self.open_files:
		fh=self.open_files[path]
		fh.flush()

	return 0

    def release(self, path, fh=None):

	print "***RELEASE: ",path

	if path in self.open_files:
		fh=self.open_files[path]
		fh.close()
		del self.open_files[path]

	return 0

    def unlink(self, path):
	
	print "***UNLINK: ",path

	if path in self.open_files:
		return -errno.ENOSYS

	os.unlink(sys.argv[-2]+path)
	return 0
	
    def rename(self, oldpath, newpath):

	os.rename(sys.argv[-2]+oldpath,sys.argv[-2]+newpath)
	return 0
	
  
if __name__ == '__main__':  
    fs = MyFS()  
    fs.parse(errex=1)  
    fs.main()  
