import os
import time

class FileLock:
	LOCK_LENGTH = 600
	
	def __init__(self, lockPath):
		self.lockPath = lockPath
	
	def isLocked(self):
		"""Checks for the lock by the lock file path. If the file is exists, the contents will be checked
		against the lock length in seconds"""
		try:
			# tries to open the lock file (and read its contents)
			lockFile = open(self.lockPath, 'r')
			try:
				lockedTime = float(lockFile.read())
			except ValueError:
				# the contents of the lock file is invalid (how can that be?)
				lockedTime = 0
		
			if (time.time() - lockedTime < self.LOCK_LENGTH):
				# a lock file is found and it's still valid
				# that means the feed is currently locked
				isLocked = True
			else:
				# the lock was issued too long ago, auto-invalidates it
				isLocked = False
		
			lockFile.close()
		except IOError:
			# problem opening the lock file, assumes no locking in place
			isLocked = False
	
		return isLocked

	def lock(self):
		"""locks it!"""
		lockFile = open(self.lockPath, 'w+')
		lockFile.write(str(time.time()))
		lockFile.close()

	def unlock(self):
		"""Unlocks it!"""
		try:
			os.remove(self.lockPath)
		except IOError:
			# do nothing in case of fail removal
			return