import glob
import os
import time
from crawling_lock import FileLock

class FileQueue:
	FILENAME_PREFIX = 'queue_'
	MAX_FILESIZE = 102400 # in bytes, equals 100KB
	existing = []
	
	def __init__(self, queueDir, lockDir):
		self.queueDir = queueDir
		self.lockDir = lockDir
		queueFiles = glob.glob(queueDir + '*')
		
		if (len(queueFiles) == 0):
			# there is no current queue
			# so simple, we will create one
			self.openNew()
		else:
			# there are some current queues
			# we must check for their locks
			freeQueueFile = False
			
			# goes through queue files
			for queueFile in queueFiles:
				queueLock = self.getFileLock(queueFile)
				if (queueLock.isLocked()):
					# the queue is being locked, ignore it
					continue
				
				if (os.path.getsize(queueFile) > self.MAX_FILESIZE):
					# the queue has grown too big, ignore it
					continue
				
				# thanks god, we found a suitable queue
				freeQueueFile = queueFile
				break
			
			if (freeQueueFile == False):
				# no free queue file is found
				# we will create a new one
				self.openNew()
			else:
				# use the found queue file
				self.open(freeQueueFile)
	
	def saveList(self, list):
		"""Saves the list to the queue for later processing"""
		intersection = []
		for item in list:
			if (item not in self.existing):
				intersection.append(item)
		
		if (len(intersection) > 0):
			# only saves if it's not empty
			self.f.write('\n'.join(intersection))
			self.f.write('\n')
			
			# also updates the in-memory queue
			self.existing.extend(intersection)
	
	def readExisting(self, queueFile):
		"""Reads existing items from the queue"""
		try:
			tmpF = open(queueFile, 'r')
			
			self.existing = []
			while (True):
				line = tmpF.readline().strip()
				if (len(line) == 0): break
				self.existing.append(line)

			tmpF.close()
		except IOError:
			pass
	
	def open(self, queueFile):
		"""Opens the specified queue file and lock the associated FileLock"""
		self.readExisting(queueFile)
		self.f = open(queueFile, 'a')
		self.queueLock = self.getFileLock(queueFile)
		self.queueLock.lock()
	
	def openNew(self):
		"""Select a new queue file name and calls self.openFile"""
		self.open(self.queueDir + self.FILENAME_PREFIX + str(int(time.time())))
	
	def getFileLock(self, queueFile):
		"""Gets the FileLock for the specified queue file"""
		return FileLock(self.lockDir + os.path.basename(queueFile))
	
	def close(self):
		"""Closes the file handler and unlocks the FileLock"""
		self.f.close()
		self.queueLock.unlock()

def main():
	print 'This script is not supposed to be run by itself.'

if (__name__ == '__main__'):
	main()