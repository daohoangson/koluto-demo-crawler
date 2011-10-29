import glob
import os
import time
from crawling_lock import FileLock

class FileQueue:
	FILENAME_PREFIX = 'queue_'
	
	def __init__(self, queueDir, lockDir):
		self.queueDir = queueDir
		self.lockDir = lockDir
		queueFiles = glob.glob(queueDir + '*')
		
		if (len(queueFiles) == 0):
			# there is no current queue
			# so simple, we will create one
			self.openNewFile()
		else:
			# there are some current queues
			# we must check for their locks
			freeQueueFile = False
			
			# goes through queue files
			for queueFile in queueFiles:
				queueLock = self.getFileLock(queueFile)
				if (queueLock.isLocked() == False):
					# thanks god, we found an unlock queue
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
		self.f.write('\n'.join(list))
	
	def open(self, queueFile):
		"""Opens the specified queue file and lock the associated FileLock"""
		self.f = open(queueFile, 'a')
		self.queueLock = self.getFileLock(queueFile)
		self.queueLock.lock()
	
	def openNew(self):
		"""Select a new queue file name and calls self.openFile"""
		self.openFile(self.queueDir + self.FILENAME_PREFIX + str(time.time()))
	
	def getFileLock(self, queueFile):
		"""Gets the FileLock for the specified queue file"""
		return FileLock(self.lockDir + os.path.basename(queueFile))
	
	def close(self):
		"""Closes the file handler and unlocks the FileLock"""
		self.f.close()
		self.queueLock.unlock()

def main():
	queue = FileQueue('./', './')
	queue.saveList(['a', 'b', 'c'])
	queue.close()

if __name__ == '__main__':
	main()