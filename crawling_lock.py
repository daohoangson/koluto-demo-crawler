def isLocked(lockPath, lockLength):
	"""Checks for the lock by the lock file path. If the file is exists, the contents will be checked
	against the lock length in seconds"""
	try:
		# tries to open the lock file (and read its contents)
		lockFile = open(lockPath, 'r')
		try:
			lockedTime = float(lockFile.read())
		except ValueError:
			# the contents of the lock file is invalid (how can that be?)
			lockedTime = 0
		
		if (time.time() - lockedTime < lockLength):
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

def lock(lockPath):
	lockFile = open(lockPath, 'w+')
	lockFile.write(str(time.time()))
	lockFile.close()

def unlock(lockPath):
	try:
		os.remove(lockPath)