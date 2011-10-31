import glob
import os
import resource
import signal
import sys
import time
import urllib
import xml.etree.ElementTree
from crawling_lock import FileLock
from crawling_queue import FileQueue

DIR_FEED_LISTS = './feed-lists/'
DIR_LOCKS = './locks/'
DIR_QUEUE = './queue/'
SLEEP_TIME = 60 # in seconds
FLAG_SLEEPING = False
FLAG_EXIT_NOW = False

def DEBUG(msg):
	print msg

def readFeed(feedUrl, feedMode, feedModeConfig):
	"""Processes feed from its url, mode and mode configuration. Return a list of links"""
	DEBUG('Reading %s (mode: %s)' % (feedUrl, feedMode))
	
	links = []
	
	try:
		feedContents = urllib.urlopen(feedUrl).read()
		
		if (feedMode == 'XPath'):
			# we are processing XPath mode
			# in this mode, the feed contents will be treated as XML
			# then we will find all elements which match the XPath in the feedModeConfig
			xmlObj = xml.etree.ElementTree.fromstring(feedContents)
			links = [link.text for link in xmlObj.findall(feedModeConfig)]
	except:
		pass
	
	return links

def main():
	global FLAG_SLEEPING # will be set True if sleeping
	
	# get the list of feeds from the 'feeds' directory in the same directory with this script
	feedLists = glob.glob(DIR_FEED_LISTS + '*')
	
	while (True):
		# get the file queue for this run (this will lock the queue until it finishes)
		feedQueue = FileQueue(DIR_QUEUE, DIR_LOCKS)

		# goes through feeds
		for feedList in feedLists:
			feedLock = FileLock(DIR_LOCKS + os.path.basename(feedList))
	
			if (feedLock.isLocked() == False):
				# the feed is not locked atm, we may proceed...
				# but first, we have to lock it
				feedLock.lock()

				try:
					feedFile = open(feedList, 'r')
					DEBUG('Processing %s' % feedList)
					
					feedUrls = feedFile.readline().strip().split(',')
					feedMode = feedFile.readline().strip()
					feedModeConfig = feedFile.readline().strip()
		
					for feedUrl in feedUrls:
						links = readFeed(feedUrl.strip(), feedMode, feedModeConfig)
						feedQueue.saveList(links)
				except IOError:
					pass
		
				# removes the lock for other sessions
				feedLock.unlock()
			else:
				# oops, it's locked atm
				DEBUG('Bypassed %s because it is being locked.' % feedList)

		# frees the file queue
		feedQueue.close()
		
		# checks if SIGINT is sent to this script
		if (FLAG_EXIT_NOW):
			print 'Stopping now!'
			break
		
		FLAG_SLEEPING = True
		DEBUG('Sleeping for %d seconds' % SLEEP_TIME)
		time.sleep(SLEEP_TIME)
	
	print 'Bye bye'

def signalHandler(signal, frame):
	global FLAG_EXIT_NOW # will be set True if can not exit immediately
	
	if (FLAG_SLEEPING):
		# the main() is sleeping (between cycles)
		# we can safely exit now
		print 'SIGINT received. Exiting immediately.'
		sys.exit(1)
	else:
		# a cycle is running, we will schedule a stop
		FLAG_EXIT_NOW = True
		print 'SIGINT received. Will halt once the current cycle is complete...'

if (__name__ == '__main__'):
	signal.signal(signal.SIGINT, signalHandler)
	main()